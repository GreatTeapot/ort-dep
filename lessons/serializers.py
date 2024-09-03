from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import *


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answers
        fields = ('id', 'answer_text')


class QuestionsSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Questions
        fields = ('id', 'question_text', 'type', 'answers')

    def get_answers(self, obj):
        answers_queryset = obj.answers.all()
        serialized_answers = AnswerSerializer(answers_queryset, many=True).data
        return serialized_answers

class TestsSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Tests
        fields = ('id', 'name', 'passed', 'time', 'questions')

    def get_questions(self, obj):
        test_questions = TestQuestions.objects.filter(test=obj)
        question_data = [QuestionsSerializer(tq.question).data for tq in test_questions]
        return question_data

class CategorySerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Topics
        fields = ('id', 'name', 'questions')

    def get_questions(self, obj):
        questions = Questions.objects.filter(topic=obj)
        return [question.question_text for question in questions]

class SubjectsSerializer(serializers.ModelSerializer):
    tests = serializers.SerializerMethodField()

    class Meta:
        model = Subjects
        fields = ('id', 'name', 'tests')

    def get_tests(self, obj):
        tests = Tests.objects.filter(subject=obj)
        return [test.name for test in tests]

class TestQuestionsSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()

    class Meta:
        model = TestQuestions
        fields = ('id', 'test', 'question')

    def get_question(self, obj):
        question_serializer = QuestionsSerializer(obj.question)
        return question_serializer.data


class ResultAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultAnswer
        fields = ('id', 'result', 'question', 'is_correct')


class ResultAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultAnalysis
        fields = ('id', 'topic', 'user', 'result', 'correct_answer', 'total_questions', 'data_recorded')
        read_only_fields = ('id', 'data_recorded')

    def create(self, validated_data):
        result_analysis = ResultAnalysis.objects.create(
            topic=validated_data['result'].test.subject,
            user=validated_data['result'].user,
            result=validated_data['result'],
            correct_answer=validated_data['correct_answer'],
            total_questions=validated_data['total_questions']
        )
        return result_analysis

class TestDetailSerializer(serializers.ModelSerializer):
    questions = QuestionsSerializer(many=True, read_only=True)

    class Meta:
        model = Tests
        fields = ('id', 'name', 'questions')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = ('id', 'user', 'test', 'start_time', 'end_time', 'score', 'scheduled_end_time')

    def create(self, validated_data):

        test = validated_data['test']
        start_time = timezone.now()
        end_time = start_time + test.time
        return Results.objects.create(
            user=validated_data['user'],
            test=test,
            start_time=start_time,
            end_time=end_time,
            scheduled_end_time=end_time,
            score=0
        )

    def update(self, instance, validated_data):
        # if timezone.now() > instance.scheduled_end_time:
        #     raise ValidationError("You missed the deadline. Test has been invalidated.")
        #
        # existing_answers_count = ResultAnswer.objects.filter(result=instance).count()
        # if existing_answers_count > 0:
        #     raise ValidationError("Answers for this result have already been submitted.")

        for answer_data in validated_data.get('answers', []):
            question = get_object_or_404(Questions, id=answer_data['question'])
            selected_answer = question.answers.filter(id=answer_data['answer']).first()
            is_correct = selected_answer.is_correct if selected_answer else False
            ResultAnswer.objects.create(result=instance, question=question, is_correct=is_correct)

            if is_correct:
                instance.score += 1

        instance.save()
        if instance.score >= instance.test.max_score:
            instance.test.passed = True
            instance.test.save()

        result_analysis_data = {
            'correct_answer': instance.score,
            'total_questions': instance.test.test_questions.count(),
            'results': instance
        }
        result_analysis_serializer = ResultAnalysisSerializer(data=result_analysis_data)
        result_analysis_serializer.is_valid(raise_exception=True)
        result_analysis_serializer.save()




# from django.shortcuts import get_object_or_404
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
#
# from .models import *
#
#
# class AnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Answers
#         fields = ('id', 'answer_text', 'is_correct')
#
#
# class QuestionsSerializer(serializers.ModelSerializer):
#     answers = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Questions
#         fields = ('id', 'question_text', 'type', 'answers')
#
#     def get_answers(self, obj):
#         answers_queryset = obj.answers.all()
#         serialized_answers = AnswerSerializer(answers_queryset, many=True).data
#         return serialized_answers
#
#
# class TestsSerializer(serializers.ModelSerializer):
#     questions = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Tests
#         fields = ('id', 'name', 'passed', 'time', 'questions')
#
#     def get_questions(self, obj):
#         test_questions = TestQuestions.objects.filter(test=obj)
#         question_data = []
#
#         for test_question in test_questions:
#             question = test_question.question
#             question_serializer = QuestionsSerializer(question)
#             question_data.append(question_serializer.data)
#
#         return question_data
#
#
# class CategorySerializer(serializers.ModelSerializer):
#     questions = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Topics
#         fields = ('id', 'name', 'questions')
#
#     def get_questions(self, obj):
#         questions = Questions.objects.filter(topic=obj)
#         question_texts = questions.values_list('question_text', flat=True)
#
#         return list(question_texts)
#
#
# class SubjectsSerializer(serializers.ModelSerializer):
#     tests = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Subjects
#         fields = ('id', 'name', 'tests')
#
#     def get_tests(self, obj):
#         tests = Tests.objects.filter(subject=obj)
#         return [test.name for test in tests]
#
#
# class TestQuestionsSerializer(serializers.ModelSerializer):
#     question = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TestQuestions
#         fields = ('id', 'test', 'question')
#
#     def get_question(self, obj):
#         question = obj.question
#         question_serializer = QuestionsSerializer(question, many=True)
#         return question_serializer.data
#
#
# class ResultAnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ResultAnswer
#         fields = ('id', 'result', 'question', 'is_correct')
#
#
# class ResultAnalysisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ResultAnalysis
#         fields = ('id', 'topic', 'user', 'result', 'correct_answer', 'total_questions', 'data_recorded')
#         read_only_fields = ('id', 'data_recorded')
#
#     def create(self, validated_data):
#         correct_answer = validated_data.get('correct_answer')
#         total_questions = validated_data.get('total_questions')
#         result = validated_data.get('result')
#
#         result_analysis = ResultAnalysis.objects.create(
#             topic=result.test.subject,
#             user=result.user,
#             result=result,
#             correct_answer=correct_answer,
#             total_questions=total_questions
#         )
#
#         return result_analysis
#
#
# class TestDetailSerializer(serializers.ModelSerializer):
#     questions = QuestionsSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Tests
#         fields = ('id', 'name', 'questions')
#
#
# class ResultSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Results
#         fields = ('id', 'test', 'start_time', 'end_time', 'score', 'scheduled_end_time')
#
#     def create(self, validated_data):
#         user = validated_data.get('user')
#         test = validated_data.get('test')
#
#         start_time = timezone.now()
#         end_time = start_time + test.time
#         result = Results.objects.create(
#             user=user,
#             test=test,
#             start_time=start_time,
#             end_time=end_time,
#             scheduled_end_time=end_time,
#             score=0
#         )
#         return result
#
#     def update(self, instance, validated_data):
#         answers_data = validated_data.pop('answers', [])
#         if timezone.now() > instance.scheduled_end_time:
#             raise ValidationError("You missed the deadline. Test has been invalidated.")
#
#         existing_answers_count = ResultAnswer.objects.filter(result=instance).count()
#         if existing_answers_count > 0:
#             raise ValidationError("Answers for this result have already been submitted.")
#
#         for answer_data in answers_data:
#             question_id = answer_data.get('question')
#             answer_id = answer_data.get('answer')
#             question = get_object_or_404(Questions, id=question_id)
#             selected_answer = question.answers.filter(id=answer_id).first()
#
#             if selected_answer is None:
#                 is_correct = False
#             else:
#                 is_correct = selected_answer.is_correct
#
#             ResultAnswer.objects.create(result=instance, question=question, is_correct=is_correct)
#
#             if is_correct:
#                 instance.score += 1
#
#         instance.save()
#
#         if instance.score >= instance.test.pass_score:
#             instance.test.passed = True
#             instance.test.save()
#
#         result_analysis_data = {
#             'correct_answer': instance.score,
#             'total_questions': instance.test.test_questions.count(),
#             'result': instance,
#         }
#         result_analysis_serializer = ResultAnalysisSerializer(data=result_analysis_data)
#         if result_analysis_serializer.is_valid():
#             result_analysis_serializer.save()
#         else:
#             raise ValidationError(result_analysis_serializer.errors)
#
#         return instance