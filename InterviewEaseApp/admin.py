from django.contrib import admin
from .models import Domain, Interview, Questions, Answers, FeedbackReport

# Admin configuration for Domain
class DomainAdmin(admin.ModelAdmin):
    search_fields = ('domain',)  # Add fields for searching in Domain

# Admin configuration for Interview
class InterviewAdmin(admin.ModelAdmin):
    search_fields = ('id', 'domain__domain')  # Add fields for searching in Interview

# Admin configuration for Questions
class QuestionsAdmin(admin.ModelAdmin):
    search_fields = ('question_text', 'interview__id')  # Add fields for searching in Questions

# Admin configuration for Answers
class AnswersAdmin(admin.ModelAdmin):
    search_fields = ('answer_text', 'question__question_text')  # Add fields for searching in Answers

class FeedbackReportAdmin(admin.ModelAdmin):
    search_fields = ('interview__id',)  # Add fields for searching in FeedbackReport

# Register models with their respective admin configurations
admin.site.register(Domain, DomainAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Answers, AnswersAdmin)
admin.site.register(FeedbackReport, FeedbackReportAdmin)
