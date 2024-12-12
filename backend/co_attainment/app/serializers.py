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

class AnswerSheetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerSheet
        fields = ['student', 'handling_staff', 'uploaded_staff', 'subject', 'year', 'semester', 'exam_type', 'marks', 'total_mark', 'course_outcome', 'file']

    def validate_file(self, value):
        # Ensure the uploaded file is an image
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("Upload a valid image file.")
        return value

    # def create(self, validated_data):
    #     request = self.context.get('request')  # Retrieve the request object
    #     staff = self.context.get('staff')
    #     answer_sheet = AnswerSheet.objects.create(**validated_data)

    #     # Create the ActivityLog entry for the creation of the AnswerSheet
    #     if request:  # Ensure the request is available
    #         activity_type = 'created'
    #         ActivityLog.objects.create(
    #             staff=staff,  # Accessing the staff from the request
    #             activity_type=activity_type,
    #             answer_sheet=answer_sheet
    #         )

    #     return answer_sheet
class AnswerSheetSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    handling_staff = StaffSerializer()
    uploaded_staff = StaffSerializer()
    subject = SubjectSerializer()
    course_outcome = CourseOutcomeSerializer(many=True)  # Assuming a many-to-many relationship for course outcomes

    class Meta:
        model = AnswerSheet
        fields = ['id', 'student', 'handling_staff', 'uploaded_staff', 'subject', 'year', 'semester', 'exam_type', 'marks', 'total_mark', 'course_outcome', 'file']

    def validate_file(self, value):
        # Ensure the uploaded file is an image
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("Upload a valid image file.")
        return value

    def create(self, validated_data):
        return AnswerSheet.objects.create(**validated_data)