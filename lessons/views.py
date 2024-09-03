from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from regauth.models import CustomUser
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *


@extend_schema(tags=['Test'])
class TestStartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultSerializer

    def get(self, request, *args, **kwargs):
        test_id = kwargs.get('id')
        test_instance = get_object_or_404(Tests, id=test_id)
        if not test_instance.time:
            return Response({"error": "Test duration is not set."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResultSerializer(data={'user': request.user.id, 'test': test_instance.id})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        test_questions = TestQuestions.objects.filter(test=test_instance)
        serialized_questions = QuestionsSerializer([tq.question for tq in test_questions], many=True).data

        time_remaining = result.scheduled_end_time - timezone.now()
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        remaining_text = f"you have {hours} hour, {minutes} min" if hours > 0 else f"you have {minutes} min"

        return Response(
            {"message": "Test started successfully.", "result_id": result.id, "remaining_time": remaining_text,
             "questions": serialized_questions}, status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Result'])
class ResultAnswersView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultSerializer

    @extend_schema(
        responses={
            200: {
                "example": {
                    "answers": [
                        {"question": 1, "answer": 2},
                        {"question": 2, "answer": 3},
                    ]
                }
            }
        }
    )
    def post(self, request, *args, **kwargs):
        result_id = kwargs.get('id')
        result = get_object_or_404(Results, id=result_id)  # Get a single Result instance

        # Check if the test time has passed or if answers have already been submitted
        if timezone.now() > result.scheduled_end_time:
            return Response({"error": "You missed the deadline. Test has been invalidated."}, status=status.HTTP_400_BAD_REQUEST)

        if ResultAnswer.objects.filter(result=result).exists():
            return Response({"error": "Answers for this result have already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize score
        score = 0

        # Process each answer
        for answer_data in request.data.get('answers', []):
            question = get_object_or_404(Questions, id=answer_data['question'])
            selected_answer = question.answers.filter(id=answer_data['answer']).first()
            is_correct = selected_answer.is_correct if selected_answer else False
            # Create the ResultAnswer instance directly
            ResultAnswer.objects.create(result=result, question=question, is_correct=is_correct)

            if is_correct:
                score += 1

        # Update result score
        result.score = score
        result.save()

        # Check if the test is passed
        if result.score >= result.test.max_score:
            result.test.passed = True
            result.test.save()

        # Create result analysis
        result_analysis_data = {
            'correct_answer': result.score,
            'total_questions': result.test.test_questions.count(),
            'result': result.pk,  # Send only the primary key value
        }
        result_analysis_serializer = ResultAnalysisSerializer(data=result_analysis_data)
        result_analysis_serializer.is_valid(raise_exception=True)
        result_analysis_serializer.save()

        return Response(result_analysis_serializer.data, status=status.HTTP_200_OK)


# @extend_schema(tags=['Result'])
# class ResultAnswersView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ResultSerializer
#
#     @extend_schema(
#         responses={
#             200: {
#                 "example": {
#                     "answers": [
#                         {"question": 1, "answer": 2},
#                         {"question": 2, "answer": 3},
#                     ]
#                 }
#             }
#         }
#     )
#     def post(self, request, *args, **kwargs):
#         result_id = kwargs.get('id')
#         result = get_object_or_404(Results, id=result_id)
#
#         serializer = ResultSerializer(data=request.data, instance=result, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(serializer.data, status=status.HTTP_200_OK)

@method_decorator(cache_page(60 * 15), name='dispatch')
@extend_schema(tags=['Lessons'])
class LessonsGetApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Subjects.objects.all()
    serializer_class = SubjectsSerializer

@method_decorator(cache_page(60 * 15), name='dispatch')
@extend_schema(tags=['Lessons'])
class LessonSearch(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Subjects.objects.all()
    serializer_class = SubjectsSerializer
    lookup_field = 'id'


@method_decorator(cache_page(60 * 15), name='dispatch')
@extend_schema(tags=['Category'])
class CategoryList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Topics.objects.all()
    serializer_class = CategorySerializer


@method_decorator(cache_page(60 * 15), name='dispatch')
@extend_schema(tags=['Category'])
class CategorySearch(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Topics.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        lesson_id = kwargs.get('lesson_pk')
        category_id = kwargs.get('category_id')

        try:
            category = Topics.objects.get(id=category_id, lessons=lesson_id)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Topics.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(cache_page(60 * 15), name='dispatch')
@extend_schema(tags=['Test'])
class TestView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Tests.objects.all()
    serializer_class = TestsSerializer

    def get(self, request, *args, **kwargs):
        subject_id = kwargs.get('subject_id')
        try:
            test = Tests.objects.filter(subject=subject_id)
            serializer = TestsSerializer(test, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Topics.DoesNotExist:
            return Response({"message": "Test went wrong "}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Test'])
class TestDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Tests.objects.all()
    serializer_class = TestsSerializer

    def get(self, request, *args, **kwargs):
        test_id = kwargs.get('test_id')
        try:
            test = Tests.objects.filter(id=test_id)
            serializer = TestsSerializer(test, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Topics.DoesNotExist:
            return Response({"message": "Test went wrong "}, status=status.HTTP_404_NOT_FOUND)



@method_decorator(cache_page(60 * 15), name='dispatch')
@extend_schema(tags=['Question'])
class QuestionView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer

    def get(self, request, *args, **kwargs):
        test_id = kwargs.get('test_id')
        try:
            questions = Questions.objects.filter(test_id=test_id)
            serializer = QuestionsSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Questions.DoesNotExist:
            return Response({"message": "No questions found for the test"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Test'])
class TopicQuestionsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionsSerializer

    @method_decorator(cache_page(60 * 15))  # Кэшируем на 15 минут
    def get(self, *args, **kwargs):
        topic_id = kwargs.get('topic_id')
        try:
            questions = Questions.objects.filter(topic=topic_id)
            serializers = QuestionsSerializer(questions, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Topics.DoesNotExist:
            return Response({"message": "Topic didnt find"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['User'])
class UserResultsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultSerializer

    def get(self, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            results = Results.objects.filter(user=user_id)
            serializers = ResultSerializer(results, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message":"User was not found"}, status=status.HTTP_404_NOT_FOUND)


# from django.utils.decorators import method_decorator
# from django.utils.timesince import timesince
# from django.views.decorators.cache import cache_page
# from drf_spectacular.utils import extend_schema
# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
# from .serializers import *
# from .models import *
# from rest_framework.response import Response
# from rest_framework import status
#
# from regauth.models import CustomUser
#
#
# @extend_schema(tags=['Test'])
# class TestStartView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ResultSerializer
#
#     def create(self, request, *args, **kwargs):
#         test_id = kwargs.get('id')
#         test_instance = get_object_or_404(Tests, id=test_id)
#         if not test_instance.time:
#             return Response({"error": "Test duration is not set."}, status=status.HTTP_400_BAD_REQUEST)
#
#         user = request.user
#         serializer = self.get_serializer(data={'user': user.id, 'test': test_instance.id})
#         serializer.is_valid(raise_exception=True)
#         result = serializer.save()
#
#         serialized_questions = QuestionsSerializer(result.test.test_questions.all(), many=True).data
#
#         time_remaining = result.scheduled_end_time - timezone.now()
#         hours, remainder = divmod(time_remaining.seconds, 3600)
#         minutes, _ = divmod(remainder, 60)
#         remaining_text = f"you have {hours} hour, {minutes} min" if hours > 0 else f"you have {minutes} min"
#
#         return Response(
#             {"message": "Test started successfully.", "result_id": result.id, "remaining_time": remaining_text,
#              "questions": serialized_questions}, status=status.HTTP_201_CREATED
#         )
#
#
# @extend_schema(tags=['Result'])
# class ResultAnswersView(generics.UpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ResultSerializer
#     queryset = Results.objects.all()
#     lookup_field = 'result_id'
#
#     def update(self, request, *args, **kwargs):
#         result = self.get_object()
#         serializer = self.get_serializer(result, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         total_questions = result.test.test_questions.count()
#         correct_answers = result.score
#         time_remaining_text = timesince(timezone.now(), result.scheduled_end_time)
#
#         response_data = {
#             "Correct Answers": correct_answers,
#             "Total Questions": total_questions,
#             "Remaining Time": time_remaining_text,
#         }
#
#         return Response(response_data, status=status.HTTP_200_OK)
#
#
# @extend_schema(tags=['Lessons'])
# class LessonsGetApiView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Subjects.objects.all()
#     serializer_class = SubjectsSerializer
#
#
# @extend_schema(tags=['Lessons'])
# class LessonSearch(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Subjects.objects.all()
#     serializer_class = SubjectsSerializer
#     lookup_field = 'id'
#
#
# @extend_schema(tags=['Category'])
# class CategoryList(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Topics.objects.all()
#     serializer_class = CategorySerializer
#
#
# @extend_schema(tags=['Category'])
# class CategorySearch(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Topics.objects.all()
#     serializer_class = CategorySerializer
#
#     def get(self, request, *args, **kwargs):
#         lesson_id = kwargs.get('lesson_pk')
#         category_id = kwargs.get('category_id')
#
#         try:
#             category = Topics.objects.get(id=category_id, lessons=lesson_id)
#             serializer = CategorySerializer(category)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Topics.DoesNotExist:
#             return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
#
#
# @extend_schema(tags=['Test'])
# class TestView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#
#     queryset = Tests.objects.all()
#     serializer_class = TestsSerializer
#
#     def get(self, request, *args, **kwargs):
#         subject_id = kwargs.get('subject_id')
#         try:
#             test = Tests.objects.filter(subject=subject_id)
#             serializer = TestsSerializer(test, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Topics.DoesNotExist:
#             return Response({"message": "Test went wrong "}, status=status.HTTP_404_NOT_FOUND)
#
#
# @extend_schema(tags=['Test'])
# class TestDetailView(generics.RetrieveAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Tests.objects.all()
#     serializer_class = TestsSerializer
#
#     def get(self, request, *args, **kwargs):
#         test_id = kwargs.get('test_id')
#         try:
#             test = Tests.objects.filter(id=test_id)
#             serializer = TestsSerializer(test, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Topics.DoesNotExist:
#             return Response({"message": "Test went wrong "}, status=status.HTTP_404_NOT_FOUND)
#
#
# @extend_schema(tags=['Test'])
# class TopicQuestionsListView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = QuestionsSerializer
#
#     @method_decorator(cache_page(60 * 15))  # Кэшируем на 15 минут
#     def get(self, *args, **kwargs):
#         topic_id = kwargs.get('topic_id')
#         try:
#             questions = Questions.objects.filter(topic=topic_id)
#             serializers = QuestionsSerializer(questions, many=True)
#             return Response(serializers.data, status=status.HTTP_200_OK)
#         except Topics.DoesNotExist:
#             return Response({"message": "Topic didnt find"}, status=status.HTTP_404_NOT_FOUND)
#
#
# @extend_schema(tags=['User'])
# class UserResultsView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ResultSerializer
#
#     def get(self, *args, **kwargs):
#         user_id = kwargs.get('user_id')
#         try:
#             results = Results.objects.filter(user=user_id)
#             serializers = ResultSerializer(results, many=True)
#             return Response(serializers.data, status=status.HTTP_200_OK)
#         except CustomUser.DoesNotExist:
#             return Response({"message":"User was not found"}, status=status.HTTP_404_NOT_FOUND)


# @extend_schema(tags=['Test'])
# class TestStartView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = TestsSerializer
#     queryset = Tests.objects.all()
#
#     def get(self, request, id, format=None):
#         test_instance = get_object_or_404(Tests, id=id)
#
#         if not test_instance.time:
#             return Response({"error": "Test duration is not set."}, status=status.HTTP_400_BAD_REQUEST)
#
#         user = request.user
#         start_time = timezone.now()
#         end_time = start_time + test_instance.time
#         questions = test_instance.test_questions.all()
#         result = Results.objects.create(
#             user=user,
#             test=test_instance,
#             start_time=start_time,
#             end_time=end_time,
#             scheduled_end_time=end_time,
#             score=0
#         )
#         serialized_questions = []
#         for question in questions:
#             question_data = QuestionsSerializer(question.question).data
#             serialized_questions.append(question_data)
#
#         time_remaining = end_time - start_time
#         hours, remainder = divmod(time_remaining.seconds, 3600)
#         minutes, _ = divmod(remainder, 60)
#
#         if hours > 0:
#             remaining_text = f"you have {hours} hour, {minutes} min"
#         else:
#             remaining_text = f"you have {minutes} min"
#
#         return Response(
#             {"message": "Test started successfully.", "result_id": result.id, "remaining_time": remaining_text,
#              "questions": serialized_questions}, status=status.HTTP_201_CREATED)
#
#
# @extend_schema(tags=['Result'])
# class ResultAnswersView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ResultAnswerSerializer
#
#     def post(self, request, result_id, format=None):
#         result = get_object_or_404(Results, id=result_id)
#
#         if timezone.now() > result.scheduled_end_time:
#             return Response({"error": "You missed the deadline. Test has been invalidated."}, status=status.HTTP_400_BAD_REQUEST)
#
#         existing_answers_count = ResultAnswer.objects.filter(result=result).count()
#         if existing_answers_count > 0:
#             return Response({"error": "Answers for this result have already been submitted."}, status=status.HTTP_400_BAD_REQUEST)
#
#         answers = request.data.get('answers', [])
#         test_questions = result.test.test_questions.all()
#         if not isinstance(answers, list):
#             return Response({"error": "Invalid format for answers"}, status=status.HTTP_400_BAD_REQUEST)
#
#         for answer_data in answers:
#             question_id = answer_data.get('question')
#             answer_id = answer_data.get('answer')
#
#             try:
#                 question = get_object_or_404(Questions, id=question_id)
#
#                 selected_answer = question.answers.filter(id=answer_id).first()
#
#                 if selected_answer is None:
#                     # If answer_id does not match any valid answer for the question, mark as incorrect
#                     is_correct = False
#                 else:
#                     is_correct = selected_answer.is_correct
#
#                 # selected_answer = Answers.objects.get(id=answer_id, question=question)
#
#                 ResultAnswer.objects.create(result=result, question=question, is_correct=is_correct)
#
#                 if is_correct:
#                     result.score += 1
#
#             except (Questions.DoesNotExist, ResultAnswer.DoesNotExist) as e:
#                 raise ValidationError("Invalid question or answer ID") from e
#
#         result.save()
#
#         result.test.passed = True
#         result.test.save()
#
#         total_questions = len(test_questions)
#         correct_answers = result.score
#         result_analysis_data = {
#             'correct_answer': correct_answers,
#             'total_questions': total_questions,
#             'result': result.id,
#         }
#
#         result_analysis_serializer = ResultAnalysisSerializer(data=result_analysis_data)
#         if result_analysis_serializer.is_valid():
#             result_analysis_serializer.save()
#         else:
#             return Response(result_analysis_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         remaining_time = result.scheduled_end_time - timezone.now()
#         time_remaining_text = timesince(timezone.now(), result.scheduled_end_time)
#
#         response_data = {
#             "Correct Answers": correct_answers,
#             "Total Questions": total_questions,
#             "Remaining Time": time_remaining_text,
#         }
#
#         return Response(response_data, status=status.HTTP_200_OK)
