# -*- coding:utf-8 -*-

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from assignments.models import (Task, TaskProgressStatus, Enrollment, EnrollmentFeedback, Resource)
from api.generic.serializers import (TaskModelSerializer, EnrollmentModelSerializer, TaskProgressStatusModelSerializer, EnrollmentFeedbackModelSerializer, ResourceModelSerializer)
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from api.studentportal.pagination import (ResourcePagination, )
from api.studentportal.serializers import StudentPortalResourceModelSerializer
from django.db.models import F


class TasksDetailModelViewSet(ModelViewSet):
    serializer_class = TaskModelSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_student:
            return Task.objects.filter(lesson__in=Enrollment.objects.filter(student_id=self.request.user.id).values_list('module__lessons', flat=True))
        else:
            return Task.objects.none()
        
    def list(self, request):
        total_completed_tasks_count = TaskProgressStatus.objects.filter(student_id=self.request.user.id, date_completed__isnull=False, date_started__isnull=False).count()
        total_tasks_count = self.get_queryset().count()
        total_pending_tasks_count = TaskProgressStatus.objects.filter(student_id=self.request.user.id, date_completed__isnull=True, date_started__isnull=False).count()
        
        return Response({'completed_tasks': total_completed_tasks_count, 'pending_tasks': total_pending_tasks_count, 'total_tasks': total_tasks_count}, status=status.HTTP_200_OK)


class EnrollmentDetailModelViewSet(ModelViewSet):
    serializer_class = EnrollmentModelSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_student:
            return Enrollment.objects.filter(student_id=self.request.user.id)
        else:
            return Enrollment.objects.none()

    def list(self, request):
        completed_enrollment_count = self.get_queryset().filter(enrollment_status="COMPLETED").count()
        rejected_enrollment_count = self.get_queryset().filter(enrollment_status="RE-SUBMIT").count()
        inreview_enrollment_count = self.get_queryset().filter(enrollment_status="IN-REVIEW").count()
        late_enrollment_count = self.get_queryset().filter(enrollment_status="COMPLETED", date_completed__gt=F('date_due')).count()
        ontime_enrollment_count = self.get_queryset().filter(enrollment_status="COMPLETED", date_due=F('date_completed')).count()
        monthly_completed_enrollment_count = list()
        for month_count in range(1,datetime.now().month + 1):
            count = self.get_queryset().filter(date_completed__month=month_count, enrollment_status="COMPLETED").count()
            monthly_completed_enrollment_count.append(count)
        return Response({'completed_enrollments': completed_enrollment_count, 'resubmit_enrollments': rejected_enrollment_count,
                         'late_submitted_enrollments': late_enrollment_count, 'ontime_submitted_enrollments': ontime_enrollment_count,
                         'inreview_enrollments': inreview_enrollment_count, 'monthly_completed_enrollment_count': monthly_completed_enrollment_count}, status=status.HTTP_200_OK)


class LastSevenDaysTasksDetailModelViewSet(ModelViewSet):
    serializer_class = TaskProgressStatusModelSerializer
    permission_class = (IsAuthenticated,)
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_student:
            return TaskProgressStatus.objects.filter(student_id=self.request.user.id)
        else:
            return TaskProgressStatus.objects.none()

    def list(self, request):
        day_start = timezone.now().replace(hour=0,minute=0, second=0) 
        day_end = timezone.now().replace(hour=23, minute=59, second=59)
        last_seven_days_completed_tasks = list()
        for day_count in range(6,-1,-1):
            count = self.get_queryset().filter(date_completed__range=(day_start - timezone.timedelta(days=day_count), day_end - timezone.timedelta(days=day_count))).count()
            last_seven_days_completed_tasks.append(count)
        return Response({'last_seven_days_completed_tasks': last_seven_days_completed_tasks}, status=status.HTTP_200_OK)


class CompletedEnrollmentFeedbackModelViewSet(ModelViewSet):
    serializer_class = EnrollmentFeedbackModelSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['get', 'head', 'options']
    
    def get_queryset(self):
        if self.request.method == 'GET':
            if self.request.query_params.get('moduleID', None) and self.request.query_params.get('studentID', None):
                return EnrollmentFeedback.objects.filter(enrollment__in=Enrollment.objects.filter(module_id=self.request.query_params.get('moduleID', None),
                                                                                                  student_id=self.request.query_params.get('studentID', None)), enrollment_status="COM")
            else:
                return EnrollmentFeedback.objects.all()
        else:
            return EnrollmentFeedback.objects.all()


class ResourceModelViewSet(ModelViewSet):
    serializer_class = ResourceModelSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['get', 'head', 'options']
    pagination_class = ResourcePagination

    def get_queryset(self):
        if self.request.user.isstudent:
            return Resource.objects.filter(users=self.request.user).order_by('id').distinct()
        else:
            return Resource.objects.none()
