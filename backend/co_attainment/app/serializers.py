from rest_framework import serializers
from .models import *

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    dept = DepartmentSerializer()

    class Meta:
        model = Student
        fields = '__all__'  # Adjust based on the fields of the Student model

class StaffSerializer(serializers.ModelSerializer):
    dept = DepartmentSerializer()

    class Meta:
        model = Staff
        fields = '__all__'   # Adjust based on the fields of the Staff model

class SubjectSerializer(serializers.ModelSerializer):
    dept = DepartmentSerializer()

    class Meta:
        model = Subject
        fields = '__all__'   # Adjust based on the fields of the Subject model

class CourseOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOutcome
        fields = '__all__'   # Adjust based on the fields of the CourseOutcome model

class AnswerSheetSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    handling_staff = StaffSerializer()
    uploaded_staff = StaffSerializer()
    subject = SubjectSerializer()
    course_outcome = CourseOutcomeSerializer(many=True)  # Assuming a many-to-many relationship for course outcomes

    class Meta:
        model = AnswerSheet
        fields = ['student', 'handling_staff', 'uploaded_staff', 'subject', 'year', 'semester', 'exam_type', 'marks', 'total_mark', 'course_outcome', 'file']

    def validate_file(self, value):
        # Ensure the uploaded file is an image
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("Upload a valid image file.")
        return value

    def create(self, validated_data):
        # Extract nested data for related models
        student_data = validated_data.pop('student')
        handling_staff_data = validated_data.pop('handling_staff')
        uploaded_staff_data = validated_data.pop('uploaded_staff')
        subject_data = validated_data.pop('subject')
        course_outcome_data = validated_data.pop('course_outcome')

        # Create related objects (if they do not already exist)
        student = Student.objects.create(**student_data)
        handling_staff = Staff.objects.create(**handling_staff_data)
        uploaded_staff = Staff.objects.create(**uploaded_staff_data)
        subject = Subject.objects.create(**subject_data)

        # Create AnswerSheet object
        answer_sheet = AnswerSheet.objects.create(
            student=student,
            handling_staff=handling_staff,
            uploaded_staff=uploaded_staff,
            subject=subject,
            **validated_data  # Use other fields from validated_data
        )

        # Handle the course_outcome relationship (assuming many-to-many)
        for co_data in course_outcome_data:
            course_outcome = CourseOutcome.objects.create(**co_data)
            answer_sheet.course_outcome.add(course_outcome)

        return answer_sheet