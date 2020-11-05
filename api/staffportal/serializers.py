# -*- coding: utf-8 -*-

from rest_framework.serializers import ModelSerializer,  ValidationError, SerializerMethodField
from assignments.models import StaffDetail, Module, ModuleCategory, StudentDetail 
from discoauth.models import DiscoUser, Parent
from api.generic.serializers import ParentModelSerializer, DiscoUserModelSerializer

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
