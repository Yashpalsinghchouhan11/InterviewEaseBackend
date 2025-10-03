from rest_framework import serializers
from .models import Interview, Questions, Domain, Answers, FeedbackReport
from .models import DIFFICULTY_LEVELS

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['question_text']


class InterviewSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    domain = serializers.CharField()
    difficulty = serializers.ChoiceField(choices=DIFFICULTY_LEVELS, default='Easy')

    class Meta:
        model = Interview
        fields = ['id', 'user', 'domain', 'difficulty', 'questions']  # include id
        read_only_fields = ['id']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        domain_name = validated_data.pop('domain')
        difficulty = validated_data.pop('difficulty', 'Easy')

        # Get or create dynamic domain
        domain, _ = Domain.objects.get_or_create(domain=domain_name)

        interview = Interview.objects.create(domain=domain, difficulty=difficulty, **validated_data)

        for question_data in questions_data:
            Questions.objects.create(interview=interview, **question_data)

        return interview

class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Questions.objects.all())
    interview = serializers.PrimaryKeyRelatedField(
        queryset=Interview.objects.all(), required=False, allow_null=True
    )
    answer_text = serializers.CharField(required=False, allow_blank=True)
    audio_path = serializers.FileField(required=False)

    class Meta:
        model = Answers
        fields = ['question', 'interview', 'answer_text', 'audio_path']

    def create(self, validated_data):
        return Answers.objects.create(**validated_data)
    

class FeedbackReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackReport
        fields = [
            "interview",
            "confidence",
            "strengths",
            "weaknesses",
            "area_of_improvement",
            "suggestions",
        ]

