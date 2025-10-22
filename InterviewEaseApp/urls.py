from django.urls import path
from . import views

urlpatterns = [
    # path('media/get_questions/<str:domain>',views.Get_questions, name='get_questions'),
    path('interview/create/',views.create_interview,name="create interview"),
    path("get_questions/<str:interview_id>",views.get_questions,name="get_questions"),
    path("save_answers/",views.save_answer,name="save_answer"),
    path("fetch_interview_answers/<str:interview_id>",views.get_answers,name="get_answers"),
    path("generate_interview_questions/",views.generate_interview_questions,name="generate_interview_questions"),
    path("feedback_report/",views.feedback_report,name="feedback_report"),
    path("generate_interview_from_resume/",views.generate_interview_from_resume, name="generate_interview_from_resume")
]
