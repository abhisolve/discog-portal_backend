# -*- coding: utf-8 -*-
from rest_framework.routers import DefaultRouter
from django.urls import path
from api.staffportal import views

router = DefaultRouter()

router.register('staff-dashboard-datatable', views.StaffDashboardDataTableModelViewSet, basename='staff-dashboard-datatable')
router.register('staff-dashboard-module-category', views.StaffDashboardModalModuleCategoryModelViewSet, basename='staff-dashboard-modal-module-category')
router.register('staff-dashboard-staff-details', views.StaffDashboardStaffDetailModelViewSet, basename='staff-dashboard-staff-detail')
router.register('user-account-dashboard', views.UserAccountDashboardModelViewSet, basename="user-account-dashboard")
router.register('user-account-dashboard-parent-select-two', views.UserAccountDashboardParentSelectTwoModelViewSet, basename='user-account-dashbaord-parent-select-two')

urlpatterns = router.urls
