# -*- coding: utf-8 -*-

from rest_framework.serializers import ModelSerializer,  ValidationError
from assignments.models import (Module, ModuleCategory, ModuleLesson, StudentDetail,
                                TaskProgressStatus, Enrollment,
                                Task, QuizQuestionOption, QuizAnswer,
                                Resource, EnrollmentFeedback, StaffDetail, QuizQuestion)
from django.core.files.base import ContentFile
from discoauth.models import PasswordReset, DiscoUser, Parent


class ModuleModelSerializer(ModelSerializer):

    def validate(self, data):
        # validate status
        if self.instance:
            if data.get('status', None) == "PUBLISHED":
                if not Task.objects.filter(lesson__module__id=self.instance.id).exists():
                    raise ValidationError({'Status': "To publish a module, At least one task is required in module's associated Lessons"})
                elif Task.objects.filter(lesson__module=self.instance.id, content_type = 'QUIZ').exists():
                    quiz_tasks = Task.objects.filter(lesson__module=self.instance.id, content_type = 'QUIZ')
                    quiz_questions = QuizQuestion.objects.filter(quiz_task__in=quiz_tasks)
                    if quiz_tasks.count() != quiz_questions.distinct('quiz_task').count():
                        raise ValidationError({'status': "Module cannot be published. Please add atleast one question in every quiz type task."})
                    elif QuizQuestionOption.objects.filter(question__in=quiz_questions).distinct('question').count() != quiz_questions.count():
                        raise ValidationError({'status': "Module cannot be published. Please add atleast one option in every quiz question."})
                    else:
                        pass
            else:
                pass
        else:
            if data.get('status', None) == "PUBLISHED":
                raise ValidationError({'Status': "To publish a module, Atlese one task is required in module's associated Lessons"})
        return data

    class Meta:
        model = Module
        fields = '__all__'


class ModuleCategoryModelSerializer(ModelSerializer):
    class Meta:
        model = ModuleCategory
        fields = '__all__'


class ModuleLessonModelSerializer(ModelSerializer):
    class Meta:
        model = ModuleLesson
        fields = '__all__'


class TaskProgressStatusModelSerializer(ModelSerializer):
    class Meta:
        model = TaskProgressStatus
        fields = '__all__'

    def validate(self, data):
        super(TaskProgressStatusModelSerializer, self).validate(data)
        if self.instance:
            if self.instance.task.response_type == "FILE" and not data.get('task_response_file') and not self.instance.task_response_file:
                raise ValidationError({'task_response_file': "Task cannot be completed without a response file!"})
            elif self.instance.task.response_type == "TXT" and not data.get('task_response_text') and not self.instance.task_response_text:
                raise ValidationError({'task_response_text': "Task cannot be completed without a response text!"})
            else:
                pass
        else:
            pass
        return data


class EnrollmentModelSerializer(ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'


class TaskModelSerializer(ModelSerializer):

    def task_image_validated(self, data):
        # return true if task_file
        # either exist in the instance
        # or in the data object.
        if self.instance:
            if self.instance.task_file or data.get('task_file', None) is not None:
                return True
            else:
                return False
        else:
            if data.get('task_file', None) is None:
                return False

    def validate(self, data):
        # just to mimic the model clean method in
        # model serializer too. as it is not called
        # by model serializer
        super(TaskModelSerializer, self).validate(data)
        if data.get('content_type', None) == 'TXT' and not data.get('task_description', None):
            raise ValidationError({'task_description': 'Task Description is required for task with content type text'})
        elif data.get('content_type', None) == 'IMG' and self.task_image_validated(data) is False:
            raise ValidationError({'task_file': 'Task file is required for task with content type Image'})
        elif data.get('content_type', None) == 'PDF' and self.task_image_validated(data) is False:
            raise ValidationError({'task_file': 'Task file is required for task with content type PDF'})
        elif data.get('content_type', None) == 'TXT-IMG':
            if not data.get('task_description', None) and self.task_image_validated(data) is False:
                raise ValidationError({'task_description': 'Task Description is required for task with content type Text & Image',
                                       'task_file': 'Task file is required for task with content type Text & Image'})
            elif not data.get('task_description', None):
                raise ValidationError({'description': 'Task Description is required for task with content type Text & Image'})
            elif self.task_image_validated(data) is False:
                raise ValidationError({'task_file': 'Task file is required for task with content type Text & Image'})
            else:
                pass
        else:
            pass
        #finally return the validated data
        return data


    class Meta:
        model = Task
        fields = '__all__'


class QuizAnswerModelSerializer(ModelSerializer):

    class Meta:
        model = QuizAnswer
        fields = '__all__'


class QuizQuestionOptionModelSerializer(ModelSerializer):

    class Meta:
        model = QuizQuestionOption
        fields = '__all__'


class DiscoUserModelSerializer(ModelSerializer):

    class Meta:
        model = DiscoUser
        fields = '__all__'


class ParentModelSerializer(ModelSerializer):

    class Meta:
        model = Parent
        fields = '__all__'


class ResourceModelSerializer(ModelSerializer):
    """
    This serializer is for base resource model.
    """
    class Meta:
        model = Resource
        fields = '__all__'

    def validate(self, data):
        super(ResourceModelSerializer, self).validate(data)
        if data.get('file_type', None) == "TXT":
            data['resource_media_file'] = None
            return data
        elif data.get('file_type', None) == "PDF" or data.get('file_type', None) == "IMG":
            data['resource_text'] = None
            return data
        else:
            pass
        return data
            
class EnrollmentFeedbackModelSerializer(ModelSerializer):
    class Meta:
        model = EnrollmentFeedback
        fields = '__all__'

    def validate(self,data):
        super(EnrollmentFeedbackModelSerializer, self).validate(data)
        if data.get('enrollment_status', None) == "COM":
            enrollment = data.get('enrollment', None)
            lessons = ModuleLesson.objects.filter(module=enrollment.module)
            tasks = Task.objects.filter(lesson__in=lessons)
            count = TaskProgressStatus.objects.filter(task__in=tasks, enrollment=enrollment, rejected_count=0).count()
            if count !=  enrollment.total_tasks:
                raise ValidationError({'Enrollment': "Enrollment with rejected tasks cannot be marked completed."})
            else:
                pass
        elif data.get('enrollment_status', None) == "RES":
            enrollment = data.get('enrollment', None)
            lessons = ModuleLesson.objects.filter(module=enrollment.module)
            tasks = Task.objects.filter(lesson__in=lessons)
            count = TaskProgressStatus.objects.filter(task__in=tasks, enrollment=enrollment, rejected_count=0).count()
            if count == enrollment.total_tasks:
                raise ValidationError({'Enrollment': "Enrollment without any rejected tasks cannot be marked rejected."})
            else:
                pass
        else:
            pass
        return data


class StudentDetailModelSerializer(ModelSerializer):

    class Meta:
        model = StudentDetail
        fields = '__all__'


class StaffDetailModelSerializer(ModelSerializer):

    class Meta:
        model = StaffDetail
        fields = '__all__'


class QuizQuestionModelSerializer(ModelSerializer):

    class Meta:
        model = QuizQuestion
        fields = "__all__"
