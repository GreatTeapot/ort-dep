from datetime import timedelta

from django.db import models
from django.utils import timezone

from regauth.models import CustomUser


class Subjects(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    description = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to='question_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Topics(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='topics')
    description = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to='question_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Questions(models.Model):
    picture = models.ImageField(upload_to='question_images/', null=True, blank=True)
    question_text = models.TextField()
    TYPE_CHOICES = (
        ('single', 'Single'),
        ('multiple', 'Multiple'),
        ('writed', 'Writed'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.question_text


class Answers(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='question_images/', null=True, blank=True)


class Tests(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='tests')
    time = models.DurationField(default=timezone.timedelta(), null=True, blank=False)
    max_score = models.PositiveIntegerField(default=100)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def set_time(self, time_str):
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            self.time = duration
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM:SS.")

    def get_time_str(self):
        seconds = self.time.total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def save(self, *args, **kwargs):
        if isinstance(self.time, str):
            self.set_time(self.time)
        super().save(*args, **kwargs)


class TestQuestions(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE, blank=True, null=True, related_name='test_questions')
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, blank=True, null=True, related_name='test_associations')

    class Meta:
        unique_together = ('test', 'question')

    def __str__(self):
        return f"Test: {self.test.name} - Question: {self.question.question_text}"


class TestTopic(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE, related_name='test_topics')
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, related_name='topic_tests')

    class Meta:
        unique_together = ('test', 'topic')  # Гарантируем уникальность комбинации test и topic

    def __str__(self):
        return f"Test: {self.test.name} - Topic: {self.topic.name}"


class Results(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='results')
    test = models.ForeignKey(Tests, on_delete=models.CASCADE, blank=True, null=True, related_name='results')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    scheduled_end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Result for {self.user.username} - Score: {self.score}"


class ResultAnswer(models.Model):
    result = models.ForeignKey(Results, on_delete=models.CASCADE, blank=True, null=True, related_name='result_answers')
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, blank=True, null=True, related_name='result_associations')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Result for {self.result.user.username} - Question: {self.question.question_text}"


class ResultAnalysis(models.Model):
    topic = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='result_analysis', blank=True, null=True,)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='result_analyses')
    result = models.ForeignKey(Results, on_delete=models.CASCADE, blank=True, null=True, related_name='result_analyses')
    correct_answer = models.PositiveIntegerField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(null=True, blank=True)
    data_recorded = models.DateTimeField(default=timezone.now)


class Subscriptions(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='subscriptions')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Subscription for {self.user.username} - Status: {self.status}"
