from django.db import models
from Authentication.models import signupModel

# Choices for domain names
# INTERVIEW_DOMAINS = [
#     ('SD', 'Softwate Developer'),
#     ('PM', 'Product management'),
#     ('HR', 'Human Resource'),
#     ('DS', 'Data Science'),
#     ('CD', 'Cloud and DevOps'),
# ]
DIFFICULTY_LEVELS = [
    ('Easy', 'Easy'),
    ('Medium', 'Medium'),
    ('Hard', 'Hard'),
]

class Domain(models.Model):
    domain = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'Domains'
        verbose_name_plural = "Domains"
    
    def __str__(self) -> str:
        return f"Domain: {self.domain}"


class Interview(models.Model):
    user = models.ForeignKey(signupModel, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='Easy')
    interview_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Interviews'
        ordering = ['-interview_date']

    def __str__(self):
        return f"Interview for {self.domain} ({self.difficulty}) - {self.user.username}"

class Questions(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)

    class Meta:
        db_table = 'Questions'

    def __str__(self) -> str:
        return f"Question: {self.question_text} (Interview ID: {self.interview.id})"

class Answers(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer_text = models.TextField(null=True, blank=True) 
    audio_path = models.FileField(upload_to='answers/audio/', null=True, blank=True)

    class Meta:
        db_table = 'Answers'

    def __str__(self) -> str:
        return f"Answer to {self.question.id} (Interview ID: {self.interview.id})"
    
class FeedbackReport(models.Model):
    interview = models.OneToOneField(
        Interview,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    confidence = models.CharField(max_length=50, blank=True, null=True)   # e.g., "Confident", "Slightly Hesitant"
    strengths = models.TextField(blank=True, null=True)
    weaknesses = models.TextField(blank=True, null=True)
    area_of_improvement = models.TextField(blank=True, null=True)  # 1–2 sentences
    suggestions = models.TextField(blank=True, null=True)          # 1–2 sentences
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "FeedbackReports"

    def __str__(self):
        return f"Feedback for Interview {self.interview.id}"

