from rest_framework import serializers
from .models import *
from authentication.serializers import UserSerializer

from mimetypes import guess_type

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    dept = DepartmentSerializer(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'  # Adjust based on the fields of the Student model

class StaffSerializer(serializers.ModelSerializer):
    dept = DepartmentSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = '__all__'   # Adjust based on the fields of the Staff model

class SubjectSerializer(serializers.ModelSerializer):
    dept = DepartmentSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'   # Adjust based on the fields of the Subject model

class CourseOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOutcome
        fields = '__all__'   # Adjust based on the fields of the CourseOutcome model

class AnswerSheetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerSheet
        fields = ['id', 'student', 'handling_staff', 'uploaded_staff', 'subject', 'year', 'semester', 'exam_type', 'marks', 'total_mark', 'file']

    def validate_file(self, value):
        # Ensure the uploaded file is an image
        mime_type, _ = guess_type(value.name)
        if not mime_type or not mime_type.startswith('image/'):
            raise serializers.ValidationError("Upload a valid image file.")
        return value

class AnswerSheetSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    handling_staff = StaffSerializer(read_only=True)
    uploaded_staff = StaffSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    # course_outcome = CourseOutcomeSerializer(read_only=True)

    class Meta:
        model = AnswerSheet
        fields = ['id', 'student', 'handling_staff', 'uploaded_staff', 'subject', 'year', 'semester', 'exam_type', 'marks', 'total_mark', 'file']

    def validate_file(self, value):
        # Ensure the uploaded file is an image
        mime_type, _ = guess_type(value.name)
        if not mime_type or not mime_type.startswith('image/'):
            raise serializers.ValidationError("Upload a valid image file.")
        return value

    def create(self, validated_data):
        return AnswerSheet.objects.create(**validated_data)

class CourseOutcomeRetrieveSerializer(serializers.ModelSerializer):
    answer_sheets = AnswerSheetSerializer(many=True, read_only=True)

    class Meta:
        model = CourseOutcome
        fields = 'id', 'co_mappings', 'course_outcomes', 'answer_sheets'

class ActivityLogSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    answer_sheet = AnswerSheetSerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = '__all__'