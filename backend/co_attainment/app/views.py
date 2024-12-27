from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import action
from .models import *
from .serializers import *
# from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from modules.ocr import ocr
from modules.csv_reader import csv_reader
from modules.asymmetric_crypt.encrypt import encrypt_message
from modules.asymmetric_crypt.decrypt import decrypt_message
from modules.asymmetric_crypt.load_keys import load_private_key, load_public_key

import random, numpy as np, cv2, json, pandas as pd, base64
from mimetypes import guess_type
from cryptography.fernet import Fernet

class AnswerSheetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally, you can filter the queryset based on the logged-in user
        return AnswerSheet.objects.filter(is_deleted=False)

    def get(self, request, *args, **kwargs):
        answer_sheets = self.get_queryset()
        print(request.user.first_name)
        serializer = AnswerSheetSerializer(answer_sheets, many=True)
        # if serializer.data.get('uploaded_staff').dept.alias == 'COE':
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        # try:
            # Extract common fields
            subject = get_object_or_404(Subject, sub_code=request.data['subject'])
            year = request.data['year']
            semester = request.data['semester']
            exam_type = request.data['exam_type']
            staff = get_object_or_404(Staff, user=request.user)

            private_key = request.data.get('pr_key', None)

            # Randomly select students without duplication
            students = list(Student.objects.all())
            if len(students) < len(request.data.getlist('answer_sheets')):
                return Response({'error': 'Not enough students to assign answer sheets'}, status=status.HTTP_400_BAD_REQUEST)
            
            random.shuffle(students)

            answer_sheets_data = []
            for data in request.FILES.getlist('answer_sheets'):
                file_content = data.read()  # Read binary content
                student = students.pop()
                file_bytes = np.fromstring(file_content, np.uint8)
                answer_script_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                marks = ocr.recognize_marks(answer_script_img)
                marks = {key: int(value) for key, value in marks.items()}
                total_mark = sum(marks.values())
                marks = json.dumps(marks)
                if private_key is not None:
                    send_public_key = PublicKey.objects.get(dept=staff.dept)
                    recv_public_key = PublicKey.objects.get(dept=subject.dept)
                    loaded_private_key = load_private_key(private_key)

                    key = Fernet.generate_key()
                    cipher = Fernet(key)

                    encrypted_content = cipher.encrypt(file_content)
                    encrypted_file = ContentFile(encrypted_content, name=data.name)

                    marks = json.dumps([
                        {
                            'message': encrypt_message(
                                loaded_private_key,
                                load_public_key(send_public_key.key),
                                marks
                            ),
                            'symmetric_key': encrypt_message(
                                loaded_private_key,
                                load_public_key(send_public_key.key),
                                key
                            ),
                        },
                        {
                            'message': encrypt_message(
                                loaded_private_key,
                                load_public_key(recv_public_key.key),
                                marks
                            ),
                            'symmetric_key': encrypt_message(
                                loaded_private_key,
                                load_public_key(recv_public_key.key),
                                key
                            ),
                        }
                    ])

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
                        'file': encrypted_file,
                    })
                else:
                    return Response({'error': 'Private key missing'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = AnswerSheetCreateSerializer(data=answer_sheets_data, many=True)
            if serializer.is_valid():
                serializer = AnswerSheetSerializer(serializer.save(), many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pk, *args, **kwargs):
        print(request.user.first_name)
        try:
            # Fetch the existing answer sheet
            staff = get_object_or_404(Staff, user=request.user)
            private_key = request.data.get('pr_key', None)

            answer_sheet = AnswerSheet.objects.get(pk=pk, is_deleted=False)

            subject = answer_sheet.subject
            
            # Check if a new file is uploaded (i.e., file field has been modified)
            new_file = request.FILES.get('file', None)
            
            if new_file:
                # If the file is modified, re-run recognize_marks to update marks and total_mark
                file_content = new_file.read()
                file_bytes = np.fromstring(file_content, np.uint8)
                answer_script_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                marks = ocr.recognize_marks(answer_script_img)
                marks = {key: int(value) for key, value in marks.items()}
                total_mark = sum(marks.values())
                marks = json.dumps(marks)
                if private_key is not None:
                    send_public_key = PublicKey.objects.get(dept=staff.dept)
                    recv_public_key = PublicKey.objects.get(dept=subject.dept)
                    loaded_private_key = load_private_key(private_key)

                    key = Fernet.generate_key()
                    cipher = Fernet(key)

                    encrypted_content = cipher.encrypt(file_content)
                    encrypted_file = ContentFile(encrypted_content, name=new_file.name)
                    request.data.update({
                        'file': encrypted_file,
                    })

                    marks = json.dumps([
                        {
                            'message': encrypt_message(
                                loaded_private_key,
                                load_public_key(send_public_key.key),
                                marks
                            ),
                            'symmetric_key': encrypt_message(
                                loaded_private_key,
                                load_public_key(send_public_key.key),
                                key
                            ),
                        },
                        {
                            'message': encrypt_message(
                                loaded_private_key,
                                load_public_key(recv_public_key.key),
                                marks
                            ),
                            'symmetric_key': encrypt_message(
                                loaded_private_key,
                                load_public_key(recv_public_key.key),
                                key
                            ),
                        }
                    ])

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
        staff = get_object_or_404(Staff, user=request.user)
        print(request.user.first_name)
        private_key_data = request.data.get('pr_key', None)
        if not private_key_data:
            return Response({'error': 'Missing private key for decryption'}, status=status.HTTP_400_BAD_REQUEST)
        private_key = load_private_key(private_key_data)
        
        # Retrieve the queryset
        if staff.dept.alias == 'COE':
            answer_sheets = self.get_queryset()
        else:
            answer_sheets = self.get_queryset().filter(subject__dept=staff.dept)
        decrypted_data = []

        for answer_sheet in answer_sheets:
            # Deserialize each item
            serializer = AnswerSheetSerializer(answer_sheet)
            data = serializer.data

            # Check if 'marks' field is in the expected encrypted JSON format
            # try:
            uploaded_staff = data.get('uploaded_staff')
            # if uploaded_staff['dept']['alias'] == 'COE':
            encrypted_data = data.get('marks')
            if isinstance(encrypted_data, str):
                encrypted_data = json.loads(encrypted_data)
            
            
            if uploaded_staff['dept']['alias'] == staff.dept.alias:
                encrypted_marks = encrypted_data[0]['message']
                encrypted_key = encrypted_data[0]['symmetric_key']
            else:
                encrypted_marks = encrypted_data[1]['message']
                encrypted_key = encrypted_data[1]['symmetric_key']
            
            # Load private key from provided data
            sender_public_key = load_public_key(PublicKey.objects.get(dept=uploaded_staff['dept']['id']).key)
            decrypted_marks = decrypt_message(
                receiver_private_key=private_key,
                sender_public_key=sender_public_key,
                encrypted_data=encrypted_marks
            ).decode()

            decrypted_key = decrypt_message(
                private_key,
                sender_public_key,
                encrypted_key
            ).decode()

            # Decrypt the file using Fernet
            fernet = Fernet(decrypted_key)
            with answer_sheet.file.open('rb') as encrypted_file:
                encrypted_content = encrypted_file.read()
                decrypted_content = fernet.decrypt(encrypted_content)

            # Convert the file content to base64 for safe transport
            file_base64 = base64.b64encode(decrypted_content).decode('utf-8')
            file_url = f"data:image/jpeg;base64,{file_base64}"

            # Include the file URL in the response
            data['file_blob_url'] = file_url
            data['marks'] = json.loads(decrypted_marks)
            # except Exception as e:
            #     print(e)
            #     return Response({'error': 'Decryption failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Append decrypted item to the list
            decrypted_data.append(data)

        return Response(decrypted_data, status=status.HTTP_200_OK)
    

class CourseOutcomeView(APIView):
    permission_classes = [ permissions.IsAuthenticated ]

    def get_query_set(self):
        return CourseOutcome.objects.filter(answer_sheets__is_deleted=False)

    def post(self, request, *args, **kwargs):
        print(request.user.first_name)
        staff = get_object_or_404(Staff, user=request.user)

        sub_code = request.data.get('sub_code', None)
        dept_alias = request.data.get('dept', None)
        exam_type = request.data.get('exam_type', None)
        batch = request.data.get('batch', None)
        private_key_data = request.data.get('pr_key', None)

        co1 = request.data.get('co1', None)
        co2 = request.data.get('co2', None)
        co3 = request.data.get('co3', None)
        co4 = request.data.get('co4', None)
        co5 = request.data.get('co5', None)
        co6 = request.data.get('co6', None)

        coq = []

        if co1 is not None:
            co1_q, co1_tot = co1.split(':')
            co1_q = co1_q.split(',')
            coq.append({
                'name': 'CO1',
                'data': co1_q,
                'total': int(co1_tot),
            })

        if co2 is not None:
            co2_q, co2_tot = co2.split(':')
            co2_q = co2_q.split(',')
            coq.append({
                'name': 'CO2',
                'data': co2_q,
                'total': int(co2_tot),
            })

        if co3 is not None:
            co3_q, co3_tot = co3.split(':')
            co3_q = co3_q.split(',')
            coq.append({
                'name': 'CO3',
                'data': co3_q,
                'total': int(co3_tot),
            })

        if co4 is not None:
            co4_q, co4_tot = co4.split(':')
            co4_q = co4_q.split(',')
            coq.append({
                'name': 'CO4',
                'data': co4_q,
                'total': int(co4_tot),
            })

        if co5 is not None:
            co5_q, co5_tot = co5.split(':')
            co5_q = co5_q.split(',')
            coq.append({
                'name': 'CO5',
                'data': co5_q,
                'total': int(co5_tot),
            })

        if co6 is not None:
            co6_q, co6_tot = co6.split(':')
            co6_q = co6_q.split(',')
            coq.append({
                'name': 'CO6',
                'data': co6_q,
                'total': int(co6_tot),
            })

        print(sub_code, dept_alias, exam_type, batch, private_key_data)

        if sub_code is None or dept_alias is None or exam_type is None or batch is None or private_key_data is None:
            return Response({'error': 'Required fields are missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        private_key = load_private_key(private_key_data)

        subject = get_object_or_404(Subject, sub_code=sub_code)
        dept = get_object_or_404(Department, alias=dept_alias)

        answer_sheets = AnswerSheet.objects.filter(
            subject=subject,
            student__dept=dept,
            student__batch=batch,
            exam_type=exam_type,
            is_deleted=False
        )

        marks = []
        check_flag = True

        for answer_sheet in answer_sheets:
            course_outcome = answer_sheet.course_outcome
            if check_flag and course_outcome is not None:
                answer_sheet_ids = set(answer_sheets.values_list('id', flat=True))
                existing_answer_sheet_ids = set(course_outcome.answer_sheets.all().values_list('id', flat=True))
                if answer_sheet_ids == existing_answer_sheet_ids:
                    serializer = CourseOutcomeRetrieveSerializer(answer_sheet.course_outcome)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    check_flag = False
            else:
                check_flag = False
            serializer = AnswerSheetSerializer(answer_sheet)
            data = serializer.data

            try:
                uploaded_staff = data.get('uploaded_staff')
                encrypted_marks = data.get('marks')
                if isinstance(encrypted_marks, str):
                    encrypted_marks = json.loads(encrypted_marks)
                
                if uploaded_staff['dept']['alias'] == staff.dept.alias:
                    encrypted_marks = encrypted_marks[0]['message']
                elif len(encrypted_marks) > 1:
                    encrypted_marks = encrypted_marks[1]['message']
                else:
                    return Response({'error': 'Operation access denied'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Load private key from provided data
                decrypted_marks = decrypt_message(
                    receiver_private_key=private_key,
                    sender_public_key=load_public_key(PublicKey.objects.get(dept=uploaded_staff['dept']['id']).key),
                    encrypted_data=encrypted_marks
                )
                
                # Replace the 'marks' field with the decrypted content
                marks.append(json.loads(decrypted_marks))
            except Exception as e:
                print(e)
                return Response({'error': 'Decryption failed'}, status=status.HTTP_400_BAD_REQUEST)


        columns = (
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            '11a', '11b', '11c', '12a', '12b', '12c', '13a', '13b',
            '13c', '14a', '14b', '14c', '15a', '15b', '15c', '16a',
            '16b', '16c', '17a', '17b', '17c', '18a', '18b', '18c',
        )

        df = pd.DataFrame(marks, columns=columns)
        co_results = csv_reader.compute_co(df, coq)

        serializer = CourseOutcomeRetrieveSerializer(
            data={
                'co_mappings': coq,
                'course_outcomes': co_results,
            }
        )
        if serializer.is_valid():
            co_obj = serializer.save()
            for answer_sheet in answer_sheets:
                answer_sheet.course_outcome = co_obj
                answer_sheet.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            course_outcomes = self.get_query_set().distinct()
        else:
            staff = get_object_or_404(Staff, user=request.user)
            course_outcomes = self.get_query_set().filter(answer_sheets__subject__dept=staff.dept).distinct()
        
        serializer = CourseOutcomeRetrieveSerializer(course_outcomes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class ActivityLogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActivityLog.objects.all()
    
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            logs = self.get_queryset().order_by('-timestamp')
        else:
            staff = get_object_or_404(Staff, user=request.user)
            logs = self.get_queryset().filter(answer_sheet__subject__dept=staff.dept).order_by('-timestamp')
        
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)