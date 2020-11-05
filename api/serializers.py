# -*- coding: utf-8 -*-

from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError
from rest_framework import serializers
from assignments.models import (Module, ModuleCategory, ModuleLesson, StudentDetail,
                                TaskProgressStatus, Enrollment,
                                Task, QuizQuestionOption, QuizAnswer, Resource,
                                EnrollmentFeedback, StaffDetail, QuizQuestion)
from django.core.files.base import ContentFile
from drf_base64.serializers import ModelSerializer as B64ModelSerializer
from discoauth.models import PasswordReset, DiscoUser, Parent
from api.generic.serializers import (ModuleModelSerializer,StudentDetailModelSerializer, ModuleCategoryModelSerializer,
                                     ResourceModelSerializer, DiscoUserModelSerializer, TaskModelSerializer, ModuleLessonModelSerializer,
                                     QuizQuestionModelSerializer, QuizAnswerModelSerializer, QuizQuestionOptionModelSerializer)
import time


class CustomUserDetailModelSerializer(ModelSerializer):

    class Meta:
        model = DiscoUser
        fields = ('id', 'first_name', 'last_name', 'is_active')

    
class ContentManagerModelSerializer(ModelSerializer):
    enrolled_student_count = serializers.SerializerMethodField()
    module_category = ModuleCategoryModelSerializer()
    
    def get_enrolled_student_count(self, instance):
        return instance.get_enrolled_student_count
    
    class Meta:
        model = Module
        fields = ('id', 'title', 'short_title', 'description', 'module_category',
                  'status', 'created_at', 'cover_image','updated_at',
                  'enrolled_student_count')

###
# Quiz Response modal serializers start here
###

class CustomQuizQuestionSerializer(QuizQuestionModelSerializer):
    
    class Meta:
        model = QuizQuestion
        fields = ('id', 'question')


class CustomQuizOptionSerializer(QuizQuestionOptionModelSerializer):
    class Meta:
        model =  QuizQuestionOption
        fields = ('id', 'option_content')


class QuizResponseSerializer(QuizAnswerModelSerializer):
    question = CustomQuizQuestionSerializer()
    choices = SerializerMethodField()
    answer = SerializerMethodField()
    correct_answer = SerializerMethodField()

    def get_answer(self, instance):
        return QuizQuestionOptionModelSerializer(instance.options.all(), many=True).data

    def get_choices(self, instance):
        return CustomQuizOptionSerializer(QuizQuestionOption.objects.filter(question=instance.question).values('id', 'option_content'), many=True).data

    def get_correct_answer(self, instance):
        return CustomQuizOptionSerializer(QuizQuestionOption.objects.filter(question=instance.question, weightage__gt=0).values('id', 'option_content'), many=True).data
    
    class Meta:
        model = QuizAnswer
        fields = ('id', 'created', 'updated', 'user', 'question', 'choices', 'correct_answer', 'answer', 'task_progress_status')

###
# Quiz Response modal serializers end here
###

###
# Resource manager serializers start here
###

class ResourceManagerPageModelSerializer(ResourceModelSerializer):
    users_count = SerializerMethodField()

    def get_users_count(self, instance):
        return instance.users.count()
    
    class Meta:
        model = Resource
        fields = ('id', 'users', 'users_count', 'resource_title', 'resource_short_title', 'resource_description', 'updated', 'suggested_student_type')


class StudentsDetailByResourceSerializer(StudentDetailModelSerializer):
    user = CustomUserDetailModelSerializer()
    total_resource = SerializerMethodField()
    current_module = SerializerMethodField()

    def get_current_module(self, instance):
        return Enrollment.objects.filter(student=instance.user.id, enrollment_status="IN-PROGRESS").values_list('module__title', flat=True)

    def get_total_resource(self, instance):
        return Resource.objects.filter(users__id=instance.user.id).count()

    class Meta:
        model = StudentDetail
        fields = ('id', 'roll_number', 'student_type', 'user', 'total_resource', 'current_module')
    
###
# Resource Manager serializers end here
###

class TaskProgressStatusModelSerializer(ModelSerializer):
    class Meta:
        model = TaskProgressStatus
        fields = '__all__'
        depth = 1

    def validate(self, data):
        super(TaskProgressStatusModelSerializer, self).validate(data)
        if self.instance:
            if self.instance.task.response_type == "FILE" and not data.get('task_response_file') and not self.instance.task_response_file:
                raise ValidationError({'Response': "Task cannot be completed without a response file!"})
            elif self.instance.task.reponse_type == "TXT" and not data.get('task_response_text') and not self.instance.task_response_text:
                raise ValidationError({'Response': "Task cannot be completed without a response text!"})
            else:
                pass
        else:
            pass
        return data

class EnrollmentModelSerializer(ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
        depth = 1


class SpecificAssignmentPageSerializer(ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'




###
#custom seriaizers for enrollment feedback page serializers start here
###

class CustomTaskModelSerializer(TaskModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'task_name', 'content_type', 'response_type')


class EnrollmentFeedBackPageModelSerializer(ModelSerializer):
    duration = SerializerMethodField()
    
    def get_duration(self, instance):
        if instance.date_completed is not None:
            time_diff = instance.date_completed - instance.date_started
            return time.strftime("%H:%M:%S", time.gmtime(time_diff.seconds))
        
    task = CustomTaskModelSerializer()
    class Meta:
        model = TaskProgressStatus
        fields = ('id' ,'task', 'task_response_file', 'duration', 'date_started','task_response_text' ,'date_completed', 'rejected_count')
    
###
#custom serializers for enrollment feedback page ends here
###

# class QuizAnswerModelSerializer(ModelSerializer):
#     class Meta:
#         model = QuizAnswer
#         fields = '__all__'


# class QuizQuestionOptionModelSerializer(ModelSerializer):
#     class Meta:
#         model = QuizQuestionOption
#         fields = '__all__'


class PasswordResetModelSerializer(ModelSerializer):
    class Meta:
        model = PasswordReset
        fields = ('password_hash', )


######################
# Auth Model Serializer
# begins here.
#######################


class DiscoUserModelSerializer(ModelSerializer):
    class Meta:
        model = DiscoUser
        fields = '__all__'


class ParentModelSerializer(ModelSerializer):

    class Meta:
        model = Parent
        fields = '__all__'


###########################
# User Account Dashboard
# related serializers begins
# here.
############################

class UserAccountDashboardDiscoUserModelSerializer(ModelSerializer):
    parent = ParentModelSerializer()

    class Meta:
        model = DiscoUser
        fields = ('id', 'username', 'parent', 'first_name',
                  'last_name', 'is_active', 'student_id',
                  'email', 'student_type')


class UserAccountDashboardModelSerializer(ModelSerializer):
    """
    Serializer used to provide data for the ModelViewSet used
    to serve as API endpoint for /user-account-dashboard path
    in the application front-end.
    """
    user = UserAccountDashboardDiscoUserModelSerializer()

    class Meta:
        model = StudentDetail
        fields = ('id', 'user', 'sibling_number',
                  'student_type', 'roll_number')


class UserAccountDashboardPostRequestSerializer(ModelSerializer):
    """
    This serializer is specificaly meant to handle the post request
    of user account dashboard view.
    """

    class Meta:
        model = DiscoUser
        fields = ('id', 'first_name', 'last_name',
                  'student_id', 'email', 'is_active',
                  'student_type', 'student_id')


class UserAccountDashboardParentModalSerializer(ModelSerializer):
    """
    This seriazlier is called is used to serialize
    data when view button is clicked on the user-account-dashboard
    """
    childrens = SerializerMethodField()

    def get_childrens(self, instance):
        return UserAccountDashboardDiscoUserModelSerializer(instance.childrens.all(), many=True).data

    class Meta:
        model = Parent
        fields = ('id', 'parent_id', 'first_name',
                  'last_name', 'email', 'childrens')


class UserAccountDashboardParentSelectTwoModalSerializer(ModelSerializer):
    """
    This seriazlier is called is used to serialize
    data when view button is clicked on the user-account-dashboard
    """

    text = SerializerMethodField()
    childrens = SerializerMethodField()
    
    def get_text(self, instance):
        return instance.parent_id
    
    def get_childrens(self, instance):
        return UserAccountDashboardDiscoUserModelSerializer(instance.childrens.all(), many=True).data

    
    class Meta:
        model = Parent
        fields = ('id', 'text', 'childrens', 'parent_id',
                  'first_name', 'last_name', 'email',)


############
# studentdetail model serializers
############

class CustomStudentDetailModelSerializer(ModelSerializer):
    """
    This serializer is to provide data for assignments dashboard home page.
    """
    user = CustomUserDetailModelSerializer()
    in_review_module_total = SerializerMethodField()
    current_module = SerializerMethodField()
    next_module = SerializerMethodField()
    previous_modules = SerializerMethodField()
    
    def get_in_review_module_total(self, instance):
        return Enrollment.objects.filter(student__id=instance.user.id, enrollment_status="IN-REVIEW",
                                         module__in=StaffDetail.objects.filter(user__id=self.context['request'].user.id).values_list('assigned_modules', flat=True)).count()

    def get_current_module(self, instance):
        return Enrollment.objects.filter(student__id=instance.user.id, enrollment_status="IN-PROGRESS").values_list('module__title', flat=True)

    def get_next_module(self, instance):
        return Enrollment.objects.filter(student__id=instance.user.id, enrollment_status="NEXT-MODULE").values_list('module__title', flat=True)
    
    def get_previous_modules(self, instance):
        return Enrollment.objects.filter(student__id=instance.user.id, enrollment_status="COMPLETED",date_completed__isnull=False).order_by('-date_completed').values_list('module__title', flat=True)


    class Meta:
        model = StudentDetail
        fields = ('id', 'user', 'roll_number', 'student_type', 'in_review_module_total',
                  'current_module', 'next_module', 'previous_modules')
###########
# student detail model serializers end
###########


class ResourceModelSerializer(ModelSerializer):
    """
    This serializer is for base resource model.
    """
    class Meta:
        model = Resource
        fields = '__all__'
        depth = 1


class EnrollmentFeedbackModelSerializer(ModelSerializer):
    class Meta:
        model = EnrollmentFeedback
        fields = '__all__'

    def validate(self,data):
        super(EnrollmentFeedbackModelSerializer, self).validate(data)
        if data.get('enrollment_status', None) == "COM" or data.get('enrollment_status', None) == "RES":
            if EnrollmentFeedback.objects.filter(enrollment_status="COM", enrollment=data.get('enrollment', None)).exists():
                raise ValidationError({'Enrollment': "Completed Enrollments can only have single feedback!"})
            else:
                pass
        else:
            pass
        return data

#####################
# staff dashboard
#####################


class StaffDashboardUserDetailModelSerializer(ModelSerializer):
    access_total = SerializerMethodField()

    def get_access_total(self, instance):
        if instance.staff_detail:
            return instance.staff_detail.assigned_modules.count()
        else:
            return None
    
    class Meta:
        model = DiscoUser
        fields = ('id', 'first_name', 'last_name',
                  'email', 'access_total')


class StaffDashboardDataTableSerializer(ModelSerializer):
    """
    This serailizer is used to serialize the data for the staff
    Dashboard table
    """
    user = StaffDashboardUserDetailModelSerializer()

    class Meta:
        model = StaffDetail
        fields = '__all__'



class StaffDashboardModalModuleModelSerializer(ModelSerializer):
    """
    Serializer used by StaffDashboardModalModuleCategoryModalSerializer
    This serializer will never be used for any other purpose or any other
    serializer. It is stricly meanted for nesting purpose.
    """
    class Meta:
        model = Module
        fields = ('id', 'title')


class StaffDashboardModalModuleCategoryModelSerializer(ModelSerializer):
    """
    serializer used to supply data for the Modal Popup in the
    add user functionality of staff dashboard Page
    """
    modules = SerializerMethodField()

    def get_modules(self, instance):
        if instance.modules:
            return StaffDashboardModalModuleModelSerializer(instance.modules.all(), many=True).data
        else:
            return None

    class Meta:
        model = ModuleCategory
        fields = ('category_type', 'modules')


class StaffDashboardStaffDetailModelSerializer(ModelSerializer):
    module_categories = SerializerMethodField()
    user_data = SerializerMethodField()

    def get_user_data(self, instance):
        return DiscoUserModelSerializer(instance.user).data

    def get_module_categories(self, instance):
        return StaffDashboardModalModuleCategoryModelSerializer(ModuleCategory.objects.all(), many=True).data

    class Meta:
        model = StaffDetail
        fields = "__all__"
