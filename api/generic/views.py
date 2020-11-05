# -*- coding: utf-8 -*-

from discoauth.models import DiscoUser, PasswordReset, Parent
from assignments.models import (Module, ModuleCategory, ModuleLesson,
                                TaskProgressStatus, Enrollment,
                                Task, QuizAnswer, QuizQuestionOption,
                                StudentDetail, Resource, EnrollmentFeedback,
                                StaffDetail, QuizQuestion)
from api.generic.serializers import (ModuleModelSerializer, ModuleCategoryModelSerializer, TaskProgressStatusModelSerializer,
                                     ModuleLessonModelSerializer, EnrollmentModelSerializer,
                                     TaskModelSerializer, QuizAnswerModelSerializer, QuizQuestionOptionModelSerializer,
                                     DiscoUserModelSerializer, ResourceModelSerializer,
                                     EnrollmentFeedbackModelSerializer, StudentDetailModelSerializer, StaffDetailModelSerializer,
                                     ParentModelSerializer, QuizQuestionModelSerializer)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser

class ModuleModelViewSet(ModelViewSet):
    serializer_class = ModuleModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = Module.objects.all()


class StudentDetailModelViewSet(ModelViewSet):
    serializer_class = StudentDetailModelSerializer
    permission_classes = [IsAuthenticated,]
    queryset = StudentDetail.objects.all()
    

class ModuleCategoryModelViewSet(ModelViewSet):
    serializer_class = ModuleCategoryModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = ModuleCategory.objects.all()


class ModuleLessonModelViewSet(ModelViewSet):
    serializer_class = ModuleLessonModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = ModuleLesson.objects.all()
    

class TaskProgressStatusModelViewSet(ModelViewSet):
    serializer_class = TaskProgressStatusModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = TaskProgressStatus.objects.all()
    

class ParentModelViewSet(ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentModelSerializer
    permission_classes = [IsAuthenticated,]


class TaskModelViewSet(ModelViewSet):
    serializer_class = TaskModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = Task.objects.all()


class QuizQuestionOptionModelViewSet(ModelViewSet):
    serializer_class = QuizQuestionOptionModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = QuizQuestionOption.objects.all()


class QuizAnswerModelViewSet(ModelViewSet):
    serializer_class = QuizAnswerModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = QuizAnswer.objects.all()


class DiscoUserModelViewSet(ModelViewSet):
    queryset = DiscoUser.objects.all()
    serializer_class = DiscoUserModelSerializer
    permission_classes = [IsAuthenticated,]


class EnrollmentModelViewSet(ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentModelSerializer
    permission_classes = [IsAuthenticated,]


class ResourceModelViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceModelSerializer
    permission_classes = [IsAuthenticated,]


class EnrollmentFeedbackModelViewSet(ModelViewSet):
    queryset = EnrollmentFeedback.objects.all()
    serializer_class = EnrollmentFeedbackModelSerializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser,)


class StaffDetailModelViewSet(ModelViewSet):
    queryset = StaffDetail.objects.all()
    serializer_class = StaffDetailModelSerializer
    permission_classes = [IsAuthenticated, ]


class QuizQuestionModelViewSet(ModelViewSet):
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionModelSerializer
    permission_classes = (IsAuthenticated, )
