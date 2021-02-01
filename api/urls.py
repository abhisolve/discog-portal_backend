# -*- coding: utf-8 -*-

from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path
from api import views
from api.generic import urls as generic_api_urls
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
router = DefaultRouter()


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info( title="DiscoG API Docs", default_version='v1', description="DiscoG API documentation", terms_of_service="https://www.google.com/policies/terms/", contact=openapi.Contact(email="contact@snippets.local"), license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


router.register('custom-student-details', views.CustomStudentDetailModelViewSet, basename='custom-student-details')
router.register('assignment-table', views.AssignmentTableModelViewSet, basename='assignment-table')
router.register('user-account-dashboard', views.UserAccountDashboardModelViewSet, basename="user-account-dashboard")
router.register('in-progress-modules', views.InProgressModelViewSet, basename='in-progress-modules')
router.register('in-review-modules-table', views.ReviewModulesTableModelViewSet, basename='in-review-modules')
router.register('staff-to-student-relation-details', views.StaffToStudentRelationModelViewSet, basename='staff-to-student-relation-details')
router.register('content-manager-page', views.ContentManagerModelViewSet, basename='content-manager-page')
router.register('enrollment-feedback-page-datatable', views.EnrollmentFeedbackPageModelViewSet, basename='enrollment-feedback-page-datatable')
router.register('resource-manager-page', views.ResourceManagerPageModelViewSet, basename='resource-manager-page')
router.register('reject-task', views.RejectTask, basename='reject-task')
router.register('student-detail-by-resource', views.StudentsDetailByResourceModelViewSet, basename='student-detail-by-resource')
router.register('un-assign-students', views.UnAssignResourceModelViewSet, basename='un-assign-students')
router.register('assign-students', views.AssignResourceModelViewSet, basename='assign-students')
router.register('quiz-response', views.QuizResponseModelViewSet, basename='quiz-response')
router.register('check-answer', views.CheckAnswerModelViewSet, basename='check-response')
router.register('module-delete', views.CustomDeleteModuleModelViewSet, basename='module-delete')


urlpatterns = [
    path('user-details/', views.UserDetail.as_view(), name='user-details'),
    path('generic/', include('api.generic.urls'), name='generic'),
    path('student-portal/', include('api.studentportal.urls'), name='student-portal'),
    path('staff-portal/', include('api.staffportal.urls'), name='staff-portal'),
    path('get-module-complete-percentage/<int:pk>',
         views.GetModuleCompletePercentage.as_view(), name='get-module-complete-percentage'),
    path('get-module-lesson-complete-percentage/<int:pk>',
         views.GetModuleLessonCompletePercentage.as_view(), name='get-module-lesson-complete-percentage'),
    path('send-reset-password-link', views.SendPasswordResetLink.as_view(), name='send-reset-password-link'),
    path('reset-password', views.ResetPassword.as_view(), name='reset-password'),
    path('copy-module/<int:id>/', views.CopyModule.as_view(), name='copy-module'),
    path('set-task-start-and-complete-time', views.SetStartAndCompleteDateInTaskProgressStatus.as_view(), name='set-start-and-end-date'),
    path('generate-token', TokenObtainPairView.as_view(), name='obtain-token'),
    path('refresh-token', TokenRefreshView.as_view(), name='refresh-obtain-token'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += router.urls
