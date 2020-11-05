# -*- coding:utf-8 -*-
from django.urls import path
import discoauth.views as views


urlpatterns = [path('login/', views.LoginView.as_view(), name="login"),
               path('logout/', views.LogoutView.as_view(), name="logout"),
               path('forgot-password/', views.ForgotPasswordView.as_view(), name="forgot-password")
]
