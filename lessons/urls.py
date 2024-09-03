from django.urls import path
from .views import *

urlpatterns = [
    path('subjects/', LessonsGetApiView.as_view(), name='info'),
    path('subjects/<int:id>/', LessonSearch.as_view(), name='lesson-info'),
    path('subjects/<int:subject_id>/category/', CategoryList.as_view(), name='category-info'),
    path('subjects/<int:subject_id>/category/<int:category_id>/', CategorySearch.as_view(), name='category-search'),
    path('subjects/<int:subject_id>/tests/', TestView.as_view(), name='all-test-info'),
    path('tests/<int:id>/start/', TestStartView.as_view(), name='start-test'),
    path('tests/<int:test_id>/', TestDetailView.as_view(), name='test-detail'),
    path('results/<int:id>/answers/', ResultAnswersView.as_view(), name='result-answers'),
    path('topics/<int:topic_id>/questions/', TopicQuestionsListView.as_view(), name='topic-questions-list'),
    path('users/<int:user_id>/results/', UserResultsView.as_view(), name='user-result'),
]
