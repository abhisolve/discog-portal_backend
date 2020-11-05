# -*- coding: utf-8 -*-

from django.urls import path
from contentmanager import views


urlpatterns = [
    path('', views.HomeContentManager.as_view(), name='content-manager-home'),
    path('create-module', views.CreateModule.as_view(), name='create-module'),
    path('edit-module/<int:id>/', views.EditModule.as_view(), name='edit-module'),
    path('add-edit-quiz-questions/<int:pk>/', views.AddEditQuizQuestionsView.as_view(), name="add-edit-quiz-questions")
]
