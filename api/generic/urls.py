# -*- coding: utf-8 -*-

from rest_framework.routers import DefaultRouter
from django.urls import path
from api.generic import views

router = DefaultRouter()

router.register('module', views.ModuleModelViewSet, basename='module')
router.register('module-category', views.ModuleCategoryModelViewSet, basename='module-category')
router.register('module-lesson', views.ModuleLessonModelViewSet, basename='module-lesson')
router.register('task-progress-status', views.TaskProgressStatusModelViewSet, basename='task-progress-status')
router.register('enrollment', views.EnrollmentModelViewSet, basename='enrollment')
router.register('task', views.TaskModelViewSet, basename='task')
router.register('quiz-question-option', views.QuizQuestionOptionModelViewSet, basename='quiz-question-option')
router.register('quiz-answers', views.QuizAnswerModelViewSet, basename='quiz-answers')
router.register('student-details', views.StudentDetailModelViewSet, basename='student-details')
router.register('parents', views.ParentModelViewSet, basename="parents")
router.register('users', views.DiscoUserModelViewSet, basename="users")
router.register('resources', views.ResourceModelViewSet, basename='resources')
router.register('enrollment-feedback', views.EnrollmentFeedbackModelViewSet, basename='enrollment-feedback')
router.register('quiz-questions', views.QuizQuestionModelViewSet, basename="quiz-questions")

urlpatterns = router.urls
