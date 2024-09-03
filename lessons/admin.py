from django.contrib import admin
from django.forms import BaseInlineFormSet
from jsonschema.exceptions import ValidationError

from .admin_forms import *
from .models import *
from regauth.models import CustomUser


class SubjectsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class TopicsAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'description')
    search_fields = ('name', 'subject__name')


class AnswersAdmin(admin.ModelAdmin):
    list_display = ('answer_text', 'get_question_text', 'is_correct')
    search_fields = ('answer_text', 'question__question_text')

    def get_question_text(self, obj):
        return obj.question.question_text
    get_question_text.short_description = 'Question'


class AnswerInlineModel(admin.TabularInline):
    model = Answers
    fields = [
        'answer_text',
        'is_correct',
        'picture'
    ]


@admin.register(Questions)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text']
    inlines = [
        AnswerInlineModel,
    ]


class TestQuestionsInline(admin.TabularInline):
    model = TestQuestions
    extra = 1


class TestTopicInline(admin.TabularInline):
    model = TestTopic
    extra = 1


class TestsAdmin(admin.ModelAdmin):
    inlines = [TestQuestionsInline, TestTopicInline]

    def save_model(self, request, obj, form, change):
        obj.save()

        selected_topics = form.cleaned_data.get('topics')  # Получаем выбранные темы

        if selected_topics is not None:  # Проверяем, что selected_topics не равен None
            selected_questions = obj.test_questions.all()  # Получаем все вопросы для этого теста

            for test_question in selected_questions:
                if test_question.question.topic not in selected_topics:
                    raise ValidationError(f"Вопрос '{test_question.question}' не принадлежит выбранным темам.")

        super().save_model(request, obj, form, change)


class ResultsAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'start_time', 'end_time', 'score')
    search_fields = ('user__username', 'test__name')


class ResultAnswerAdmin(admin.ModelAdmin):
    list_display = ('result', 'get_question_text', 'is_correct')
    search_fields = ('result__user__username', 'question__question_text')

    def get_question_text(self, obj):
        return obj.question.question_text if obj.question else '-'  # Return question text or '-' if no question
    get_question_text.short_description = 'Question'


class ResultAnalysisAdmin(admin.ModelAdmin):
    list_display = ('topic', 'user', 'result', 'correct_answer', 'total_questions', 'data_recorded')
    search_fields = ('topic__name', 'user__username')


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'status')
    search_fields = ('user__username',)


admin.site.register(Subjects, SubjectsAdmin)
admin.site.register(Topics, TopicsAdmin)
# admin.site.register(Questions, QuestionAdmin)
admin.site.register(Answers, AnswersAdmin)
admin.site.register(Tests, TestsAdmin)
admin.site.register(Results, ResultsAdmin)
admin.site.register(ResultAnalysis, ResultAnalysisAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(TestQuestions)

