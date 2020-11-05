# -*- coding: utf-8 -*-
from assignments.models import (StaffDetail, ModuleCategory, StudentDetail)
from discoauth.models import DiscoUser, Parent
from api.staffportal.serializers import (StaffDashboardDataTableSerializer, StaffDashboardModalModuleCategoryModelSerializer,
                                         StaffDashboardStaffDetailModelSerializer, UserAccountDashboardModelSerializer,
                                         UserAccountDashboardParentSelectTwoModalSerializer, UserAccountDashboardParentModalSerializer,
                                         UserAccountDashboardPostRequestSerializer)
from api.generic.serializers import DiscoUserModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class StaffDashboardDataTableModelViewSet(ModelViewSet):
    queryset = StaffDetail.objects.all()
    serializer_class = StaffDashboardDataTableSerializer
    permission_classes = (IsAuthenticated, )


class StaffDashboardModalModuleCategoryModelViewSet(ModelViewSet):
    queryset = ModuleCategory.objects.all()
    serializer_class = StaffDashboardModalModuleCategoryModelSerializer
    permission_classes = (IsAuthenticated, )


class StaffDashboardStaffDetailModelViewSet(ModelViewSet):
    queryset = StaffDetail.objects.all()
    serializer_class = StaffDashboardStaffDetailModelSerializer
    permission_classes = (IsAuthenticated, )

    def pre_create(self):
        print("Pre_create is called")
        user_serializer = DiscoUserModelSerializer(data=self.request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(self.request.data.get('password', "DiscogUser"))
            return user
        else:
            print(user_serializer.errors)
            self.user_serializer_errors = user_serializer.errors
            return None

    def create(self, request, *args, **kwargs):
        try:
            staff_id = StaffDetail.objects.get(staff_id=request.data.get('staff_id', None))
            return Response({"staff_id": ["Staff ID %s already exists in database " % request.data.get('staff_id', None)]},
                            status=status.HTTP_400_BAD_REQUEST)
        except StaffDetail.DoesNotExist:
            user = self.pre_create()
            if user is not None:
                request._full_data = {'user': user.id,
                                      "staff_id": request.data.get('staff_id', None),
                                      'staff_role': request.data.get('staff_role', None),
                                      'assigned_modules': request.data.get('assigned_modules', None)}
                return super(StaffDashboardStaffDetailModelViewSet, self).create(request, *args, **kwargs)
            else:
                return Response(self.user_serializer_errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """
        custom parital update that can handle both
        the user data snd the staff details data in same.
        """
        try:
            user = DiscoUser.objects.get(id=request.data.get('user', None))
            user_serializer = DiscoUserModelSerializer(instance=user, data=request.data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DiscoUser.DoesNotExist:
            return Response({'user_id': ['Invalid User Id']}, status=status.HTTP_400_BAD_REQUEST)
        return super(StaffDashboardStaffDetailModelViewSet,self).partial_update(request, *args, **kwargs)
    

class UserAccountDashboardModelViewSet(ModelViewSet):
    queryset = StudentDetail.objects.all()
    serializer_class = UserAccountDashboardModelSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['head', 'option', 'get', 'post']

    def retrieve(self, request, pk=None):
        return Response(UserAccountDashboardParentModalSerializer(Parent.objects.get(id=pk)).data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        custom create method made to work with the
        data send by fornt-end modal popup in user-account
        view in the front-end.
        """
        print("request data is %s" % (request.data))
        parent = request.data.get('parent', None)
        valid_object_list = list()
        for key in request.data.get('to_save', {}):
            print("key is %s" % key)
            if key != "parent":
                raw_data = request.data.get('to_save', None).get(key, None)
                print("raw data is %s" % raw_data)
                raw_data['password'] = "22023801@aA"
                serializer = DiscoUserModelSerializer(data=raw_data)
                student_id = request.data.get('to_save', None).get(key, None).get('roll_number', None)
                if serializer.is_valid():
                    if StudentDetail.objects.filter(roll_number=student_id).exists():
                        return Response({'Student ID': "Student Id %s already exists" % student_id},
                                        status=status.HTTP_400_BAD_REQUEST)
                    elif student_id is None:
                        return Response({'Student Id' "Student Id is required to have in data"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        valid_object_list.append({
                            'roll_number': student_id,
                            'student_type': request.data.get('to_save', None).get(key, None).get('student_type', None),
                            'serializer': serializer})
                else:
                    return Response(serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                pass
                
        # once buck validate is done we have the data
        # in desired_format to create the
        for valid_object in valid_object_list:
            print("valid object is %s \n" % valid_object)
            user = valid_object['serializer'].save()
            # create student_details object
            StudentDetail.objects.create(roll_number=valid_object['roll_number'],
                                         student_type=valid_object['student_type'],
                                         user=user)

        # update the to update users here
        for user_id in request.data.get('to_update', {}):
            raw_data = request.data.get('to_update', None).get(user_id, None)
            print("raw data is %s" % raw_data)
            serializer = DiscoUserModelSerializer(DiscoUser.objects.get(id=user_id), data=raw_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                StudentDetail.objects.filter(user__id=user_id).update(student_type=raw_data['student_type'],
                                                                      roll_number=raw_data['roll_number'])
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # finally get all the childrens of the parent
        # and send their data as reponse back.
        user_data_serializer = UserAccountDashboardPostRequestSerializer(DiscoUser.objects.filter(parent__id=parent), many=True)
        return Response(user_data_serializer.data, status=status.HTTP_201_CREATED)


class UserAccountDashboardParentSelectTwoModelViewSet(ModelViewSet):
    """
    API used by select2 in user account dashboard page. Not for extended use
    """
    queryset = Parent.objects.all()
    serializer_class = UserAccountDashboardParentSelectTwoModalSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'option', 'head']

    def list(self, request, *args, **kwargs):
        if self.request.query_params.get('search', None):
            return Response({'results': self.serializer_class(
                Parent.objects.filter(parent_id__icontains=self.request.query_params.get('search')), many=True
            ).data}, status=status.HTTP_200_OK)
        else:
            return Response({'results': []}, status=status.HTTP_200_OK)
