from django.urls import path
from .views import *

app_name = 'app'

urlpatterns = [
    path('answersheets/get/', AnswerSheetView.as_view(), name='answersheet-read'),
    path('answersheets/decrypt/', AnswerSheetRetrieveView.as_view(), name='answersheet-decrypt-read'),

    # Bulk create endpoint for answer sheets
    path('answersheets/bulk-create/', AnswerSheetView.as_view(), name='answersheet-bulk-create'),

    # Update endpoint for a specific answer sheet
    path('answersheets/<int:pk>/', AnswerSheetView.as_view(), name='answersheet-update'),

    # Delete endpoint for a specific answer sheet
    path('answersheets/<int:pk>/delete/', AnswerSheetView.as_view(), name='answersheet-delete'),
]