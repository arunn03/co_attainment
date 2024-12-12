from django.db import models
from django.contrib.auth import get_user_model

import os

from django.shortcuts import get_object_or_404

User = get_user_model()

class Department(models.Model):
    name = models.CharField(max_length=256)
    alias = models.CharField(max_length=10)

    def __str__(self):
        return self.alias
    
class PublicKey(models.Model):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    key = models.TextField()

    def __str__(self):
        return self.dept.name

class Student(models.Model):
    name = models.CharField(max_length=256)
    roll = models.CharField(max_length=15)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()
    batch = models.PositiveIntegerField()

    def __str__(self):
        return self.roll

class Staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class Subject(models.Model):
    sub_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=256)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    credits = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

class CourseOutcome(models.Model):
    co_mappings = models.JSONField()
    course_outcomes = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AnswerSheet(models.Model):
    EXAM_TYPE_CHOICES = [
        ('MS1', 'Mid-Semester 1'),
        ('MS2', 'Mid-Semester 2'),
        ('Final', 'Final Exam'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    handling_staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='handled_answer_sheets')
    uploaded_staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='uploaded_answer_sheets')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    marks = models.JSONField()
    total_mark = models.PositiveIntegerField()
    course_outcome = models.ForeignKey(CourseOutcome, null=True, blank=True, on_delete=models.SET_NULL)
    file = models.FileField(upload_to='answer_sheets/')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.student.roll} - Year {self.year} - Semester {self.semester} - {self.exam_type} - {self.subject.name}{" (deleted)" if self.is_deleted else ""}'
    
    def delete_file(self):
        if self.file and self.file.storage.exists(self.file.name):
            self.file.delete(save=False)
    
    def save(self, *args, **kwargs):
        activity_type = 'created'

        if self.pk:
            old_instance = AnswerSheet.objects.get(pk=self.pk)
            old_file = old_instance.file
            if old_file and old_file != self.file:
                old_file.delete(save=False)

            activity_type = 'updated' if not self.is_deleted else 'deleted'

        super().save(*args, **kwargs)
        
        # staff = get_object_or_404(Staff, user=request.user)
        ActivityLog.objects.create(
            staff=self.uploaded_staff,
            activity_type=activity_type,
            answer_sheet=self
        )

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

        # super().delete(*args, **kwargs)

class ActivityLog(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('created', 'created'),
        ('updated', 'updated'),
        ('deleted', 'deleted'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPE_CHOICES)
    answer_sheet = models.ForeignKey(AnswerSheet, on_delete=models.DO_NOTHING, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.staff.user.first_name} {self.activity_type} answer sheet {self.answer_sheet.id}'
