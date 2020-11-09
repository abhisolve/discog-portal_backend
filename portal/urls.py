# -*- coding: utf-8 -*-

from portal import views
from django.urls import path


urlpatterns = [
    path('', views.Dashboard.as_view(), name="dashboard"),
    path('student-dashboard', views.StudentDashboard.as_view(), name='student-dashboard'),
    path('in-progress-module', views.InProgressModule.as_view(), name='in-progress-module'),
    path('completed-modules', views.CompletedModuleList.as_view(), name='completed-modules'),
    path('reset-password', views.ResetPassword.as_view(), name='reset-password'),
    path('assignments-dashboard', views.AssignmentsDashboard.as_view(), name='assignments-dashboard'),
    path('specific-assignments-dashboard/<int:pk>/', views.SpecificAssignmentsDashboard.as_view(), name='specific-assignments-dashboard'),
    path('user-account-dashboard', views.UserAccountDashboard.as_view(), name="user-account-dashboard"),
    path('resource', views.ResourceDashboard.as_view(), name='resource'),
    path('specific-resource/<int:pk>/', views.SpecificResourceDashboard.as_view(), name='specific-resource'),
    path('review-students', views.ReviewStudentsDashboard.as_view(), name='review-students'),
    path('review-modules/<int:pk>/', views.ReviewModulesDashboard.as_view(), name='review-modules'),
    path('staff-dashboard', views.StaffDashboardView.as_view(), name='staff-dashboard'),
    path('enrollment-feedback/<int:pk>/', views.ReviewTasksDashboard.as_view(), name='enrollment-feedback'),
    path('add-resource-page', views.AddResourcePageView.as_view(), name='add-resource-page'),
    path('view-resource/<int:pk>/', views.ViewResourcePage.as_view(),  name='view-resource'),
    path('send-reset-password-mail', views.SendResetPasswordMail.as_view(), name='send-reset-password-mail'),
    path('resource-manager', views.ResourceManagerPage.as_view(), name='resource-manager'),
    path('edit-account', views.EditStudentAccountPage.as_view(), name='edit-account'),
    path('forgot-password-page', views.ForgotPasswordPage.as_view(), name='forgot-password-page'),
    path('set-password', views.SetPasswordPage.as_view(), name='set-password'),
    path('edit-resource/<int:pk>/', views.EditResourcePage.as_view(), name='edit-resource'),
    path('platform-invite/<str:invite_hash>', views.PlatformInviteView.as_view(), name="platform-invite"),
    path('check-release', views.CheckRelease.as_view(), name='check-release'),
]
