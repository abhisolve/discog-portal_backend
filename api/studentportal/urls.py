# -*- coding: utf-8 -*-
from rest_framework.routers import DefaultRouter
from django.urls import path
from  api.studentportal import views

router = DefaultRouter()

router.register('student-tasks-data', views.TasksDetailModelViewSet, basename='student-tasks-data')
router.register('student-enrollments-data', views.EnrollmentDetailModelViewSet, basename='student-enrollments-data')
router.register('last-seven-days-task-data', views.LastSevenDaysTasksDetailModelViewSet, basename='last-seven-days-task-data')
router.register('completed-enrollment-feedback', views.CompletedEnrollmentFeedbackModelViewSet, basename='completed-enrollment-feedback')
router.register('assigned-resources-for-student', views.ResourceModelViewSet, basename='assigned-resource-for-student')

urlpatterns = router.urls
