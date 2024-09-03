from django import forms
from .models import *


class TestAdminForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(queryset=Topics.objects.all(), required=True, widget=forms.CheckboxSelectMultiple)
    questions = forms.ModelMultipleChoiceField(queryset=Questions.objects.all(), required=True, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Tests
        fields = '__all__'


class TestQuestionsAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TestQuestionsAdminForm, self).__init__(*args, **kwargs)

        self.fields['test'].queryset = Tests.objects.all()
        self.fields['question'].queryset = Questions.objects.all()

    class Meta:
        model = TestQuestions
        fields = '__all__'