from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import action
from .models import *
from .serializers import *
from django.db import transaction
from django.shortcuts import get_object_or_404
from modules.ocr import ocr
from modules.asymmetric_crypt.encrypt import encrypt_message
from modules.asymmetric_crypt.decrypt import decrypt_message
from modules.asymmetric_crypt.load_keys import load_private_key, load_public_key

import random, numpy as np, cv2, json

class AnswerSheetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally, you can filter the queryset based on the logged-in user
        return AnswerSheet.objects.filter(is_deleted=False)

    def get(self, request, *args, **kwargs):
        answer_sheets = self.get_queryset()
        serializer = AnswerSheetSerializer(answer_sheets, many=True)
        # if serializer.data.get('uploaded_staff').dept.alias == 'COE':
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        try:
            # Extract common fields
            subject = Subject.objects.get(sub_code=request.data['subject'])
            year = request.data['year']
            semester = request.data['semester']
            exam_type = request.data['exam_type']
            staff = get_object_or_404(Staff, user=request.user)

            is_encryption_enabled = staff.dept.alias == 'COE'
            private_key = request.data.get('pr_key', None)

            # Randomly select students without duplication
            students = list(Student.objects.all())
            if len(students) < len(request.data.getlist('answer_sheets')):
                return Response({'error': 'Not enough students to assign answer sheets'}, status=status.HTTP_400_BAD_REQUEST)
            
            random.shuffle(students)

            answer_sheets_data = []
            for data in request.FILES.getlist('answer_sheets'):
                student = students.pop()
                file_bytes = np.fromstring(data.read(), np.uint8)
                answer_script_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                marks = ocr.recognize_marks(answer_script_img)
                marks = {key: int(value) for key, value in marks.items()}
                total_mark = sum(marks.values())
                marks = json.dumps(marks)
                if is_encryption_enabled and private_key is not None:
                    public_key = PublicKey.objects.get(dept=subject.dept)
                    marks = json.dumps(encrypt_message(
                        load_private_key(private_key),
                        load_public_key(public_key.key),
                        marks
                    ))

                answer_sheets_data.append({
                    'student': student.id,
                    'handling_staff': staff.id,
                    'uploaded_staff': staff.id,
                    'subject': subject.id,
                    'year': year,
                    'semester': semester,
                    'exam_type': exam_type,
                    'marks': marks,
                    'total_mark': total_mark,
                    'file': data,
                    # 'course_outcome': None,
                })

            # Bulk creation inside transaction
            # with transaction.atomic():
            serializer = AnswerSheetCreateSerializer(data=answer_sheets_data, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Answersheets are created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pk, *args, **kwargs):
        try:
            # Fetch the existing answer sheet
            staff = get_object_or_404(Staff, user=request.user)
            is_encryption_enabled = staff.dept.alias == 'COE'
            private_key = request.data.get('pr_key', None)

            answer_sheet = AnswerSheet.objects.get(pk=pk, is_deleted=False)

            subject = answer_sheet.subject
            
            # Check if a new file is uploaded (i.e., file field has been modified)
            new_file = request.FILES.get('file', None)
            
            if new_file:
                # If the file is modified, re-run recognize_marks to update marks and total_mark
                file_bytes = np.fromstring(new_file.read(), np.uint8)
                answer_script_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                marks = ocr.recognize_marks(answer_script_img)
                marks = {key: int(value) for key, value in marks.items()}
                total_mark = sum(marks.values())
                marks = json.dumps(marks)
                if is_encryption_enabled and private_key is not None:
                    public_key = PublicKey.objects.get(dept=subject.dept)
                    marks = json.dumps(encrypt_message(
                        load_private_key(private_key),
                        load_public_key(public_key.key),
                        marks
                    ))

                # Update request data with new marks and total_mark
                request.data.update({
                    'uploading_staff': staff,
                    'marks': marks,
                    'total_mark': total_mark,
                })

            # Use the serializer to validate and save changes
            serializer = AnswerSheetSerializer(answer_sheet, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except AnswerSheet.DoesNotExist:
            return Response({'error': 'Answer Sheet not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, *args, **kwargs):
        try:
            answer_sheet = AnswerSheet.objects.get(pk=pk, is_deleted=False)
            answer_sheet.delete()
            return Response({'status': 'Answer Sheet deleted'}, status=status.HTTP_200_OK)
        except AnswerSheet.DoesNotExist:
            return Response({'error': 'Answer Sheet not found'}, status=status.HTTP_404_NOT_FOUND)


class AnswerSheetRetrieveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AnswerSheet.objects.filter(is_deleted=False)

    def post(self, request, *args, **kwargs):
        private_key_data = request.data.get('pr_key', None)
        
        # Retrieve the queryset
        answer_sheets = self.get_queryset()
        decrypted_data = []

        for answer_sheet in answer_sheets:
            # Deserialize each item
            serializer = AnswerSheetSerializer(answer_sheet)
            data = serializer.data

            # Check if 'marks' field is in the expected encrypted JSON format
            try:
                uploaded_staff = data.get('uploaded_staff')
                if uploaded_staff['dept']['alias'] == 'COE':
                    encrypted_marks = data.get('marks')
                    if isinstance(encrypted_marks, str):
                        encrypted_marks = json.loads(encrypted_marks)
                    if not private_key_data:
                        return Response({'error': 'Missing private key for decryption'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Load private key from provided data
                    private_key = load_private_key(private_key_data)
                    decrypted_marks = decrypt_message(
                        receiver_private_key=private_key,
                        sender_public_key=load_public_key(PublicKey.objects.get(dept=uploaded_staff['dept']['id']).key),
                        encrypted_data=encrypted_marks
                    )
                    
                    # Replace the 'marks' field with the decrypted content
                    data['marks'] = json.loads(decrypted_marks)
            except Exception as e:
                print(e)
                return Response({'error': 'Decryption failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Append decrypted item to the list
            decrypted_data.append(data)

        return Response(decrypted_data, status=status.HTTP_200_OK)