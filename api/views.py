#! -*- coding: utf-8 -*-

from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser
from assignments.models import (Module, ModuleCategory, ModuleLesson,
                                TaskProgressStatus, Enrollment,
                                Task, QuizAnswer, QuizQuestionOption, StudentDetail, Resource,
                                EnrollmentFeedback, StaffDetail)
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers import (ModuleModelSerializer, ModuleCategoryModelSerializer, ModuleLessonModelSerializer,
                             TaskProgressStatusModelSerializer, EnrollmentModelSerializer,
                             TaskModelSerializer,QuizQuestionOptionModelSerializer, QuizAnswerModelSerializer, PasswordResetModelSerializer,
                             StudentDetailModelSerializer, UserAccountDashboardModelSerializer, ParentModelSerializer,
                             UserAccountDashboardPostRequestSerializer, DiscoUserModelSerializer, UserAccountDashboardParentModalSerializer,
                             ResourceModelSerializer, EnrollmentFeedbackModelSerializer,
                             UserAccountDashboardParentSelectTwoModalSerializer, StaffDashboardDataTableSerializer,
                             StaffDashboardModalModuleCategoryModelSerializer, StaffDashboardStaffDetailModelSerializer,
                             ContentManagerModelSerializer, SpecificAssignmentPageSerializer, EnrollmentFeedBackPageModelSerializer,
                             CustomStudentDetailModelSerializer, ResourceManagerPageModelSerializer,
                             StudentsDetailByResourceSerializer, QuizResponseSerializer)
from django.db.models import F, Count
from discoauth.models import DiscoUser, PasswordReset, Parent
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from discomail.models import EmailQueue
from django.template.loader import render_to_string
from django.conf import settings
from django.http import QueryDict
from datetime import datetime
import pytz
import json

class ResourceManagerPageModelViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceManagerPageModelSerializer
    permission_classes = [IsAuthenticated, ]
    
class CustomStudentDetailModelViewSet(ModelViewSet):
    queryset = StudentDetail.objects.all()
    serializer_class = CustomStudentDetailModelSerializer
    permission_classes = [IsAuthenticated, ]
    

class EnrollmentFeedbackPageModelViewSet(ModelViewSet):
    serializer_class = EnrollmentFeedBackPageModelSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        if self.request.method == "GET":
            if self.request.query_params.get('enrollmentID', None) and self.request.query_params.get('taskID', None):
                return TaskProgressStatus.objects.filter(task_id=self.request.query_params.get('taskID', None), enrollment_id= self.request.query_params.get('enrollmentID', None))
            elif self.request.query_params.get('enrollID', None):
                return TaskProgressStatus.objects.filter(enrollment_id=self.request.query_params.get('enrollID', None), date_completed__isnull=False).exclude(task__response_type="NONE")
            else:
                return TaskProgressStatus.objects.all()
        else:
            return TaskProgressStatus.objects.all()
        
class ContentManagerModelViewSet(ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ContentManagerModelSerializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser,)
    
    def create(self, request):
        try:
            data = self.request.data
            category = ModuleCategory.objects.get(id=data.__getitem__('module_category'))
            Created_module = Module.objects.create(module_category=category,title=data.__getitem__('title'),description=data.__getitem__('description'),status=data.__getitem__('status'),
                                  short_title=data.__getitem__('short_title'),cover_image=data.__getitem__('cover_image'))
            module_serializer = ContentManagerModelSerializer(Created_module)
            return Response(module_serializer.data , status=status.HTTP_200_OK)
        except Module.DoesNotExist:
            return Response({'error':'Module not created successfully'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            update_module = Module.objects.get(id=pk)
            module_serializer = ContentManagerModelSerializer(instance=update_module, data=self.request.data, partial=True)
            category = ModuleCategory.objects.get(id=self.request.data.__getitem__('module_category'))
            if module_serializer.is_valid():
                module_serializer.save()
                Module.objects.filter(id=pk).update(module_category=category)
                return Response (module_serializer.data , status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Module not updated succesfully'}, status=status.HTTP_400_BAD_REQUEST)
        except Module.DoesNotExist:
            return Response({'error': 'Module not updated succesfully'}, status=status.HTTP_400_BAD_REQUEST)
        
class InProgressModelViewSet(ModelViewSet):
    serializer_class = EnrollmentModelSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = Enrollment.objects.filter(enrollment_status='IN-PROGRESS')

    def partial_update(self, request, pk=None):
        try:
            update_instance = self.queryset.get(student__id=pk)
            if request.data.get('completed') != "1":
                update_instance.date_to_start = timezone.now()
                update_instance.save()
                return Response ({'success': 'Start date updated'}, status=status.HTTP_200_OK)
            else:
                update_instance.date_completed = timezone.now()
                update_instance.save()
                return Response ({'success': ' date updated'}, status=status.HTTP_200_OK)
        except Enrollment.DoesNotExist:
            return Response({'error': 'date not updated'}, status=status.HTTP_400_BAD_REQUEST)
    
class EnrollmentModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    queryset = Enrollment.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EnrollmentModelSerializer
        else:
            return SpecificAssignmentPageSerializer
   
class AssignmentTableModelViewSet(ModelViewSet):
    serializer_class = EnrollmentModelSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_student:
            if self.request.query_params.get('userID', None):
                return Enrollment.objects.filter(student__id=self.request.query_params.get('userID', None))
            else:
                return Enrollment.objects.none()
        else:
            return Enrollment.objects.none()


class GetModuleCompletePercentage(APIView):
    def get(self, request, pk):
        if pk is not None:
            total_completed_modules = 0
            module_with_total_lesson_count = Module.objects.filter(
                id=pk).annotate(total_module_lessons=Count(F('lessons')))
            for lesson in module_with_total_lesson_count.values_list('lessons'):
                lesson_instance = ModuleLesson.objects.get(id=lesson[0])
                if lesson_instance.completed:
                    total_completed_modules += 1
            total_percentage_float = (total_completed_modules / module_with_total_lesson_count.values_list(
                'total_module_lessons', flat=True)[0]) * 100
            total_percentage = int(total_percentage_float)
            return Response({'success': total_percentage}, status=status.HTTP_200_OK)
        return Response({'error': 'Bad module ID'}, status=status.HTTP_400_BAD_REQUEST)


class GetModuleLessonCompletePercentage(APIView):
    def get(self, request, pk):
        if pk is not None:
            total_completed_tasks = 0
            lesson_with_total_task_count = ModuleLesson.objects.filter(
                id=pk).annotate(total_task_count=Count(F('tasks')))
            for task in lesson_with_total_task_count.values_list('tasks'):
                task_instance = Task.objects.get(id=task[0])
                if task_instance.completed:
                    total_completed_tasks += 1
            total_percentage = (total_completed_tasks / lesson_with_total_task_count.values_list(
                'total_task_count', flat=True)[0]) * 100
            return Response({'success': total_percentage}, status=status.HTTP_200_OK)
        return Response({'error': 'Bad Lesson ID'}, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordResetLink(APIView):
    """
    API view which allow to send the reset-password email
    This view is used by /auth/forgot-password page.
    """
    def post(self, request):
        email = request.data.get('email', None)
        if email is not None:
            try:
                password_reset_hash = get_random_string(length=100)
                user = DiscoUser.objects.get(email=email)
                password_reset_instance = PasswordReset.objects.create(is_active=True,
                                                                       user=user,
                                                                       password_hash=password_reset_hash)
                serialized_data = PasswordResetModelSerializer(password_reset_instance)
                EmailQueue.objects.create(subject='Reset Password',
                                          to_email=user.email,
                                          body=render_to_string('discomail/reset-password.html',
                                                                context={'data': serialized_data.data,
                                                                         'host': settings.HOST}),
                                          email_type='FPE',
                                          send_now=True)
                return Response({'Success': 'We have sent you a recovery email.'}, status=status.HTTP_200_OK)
            except DiscoUser.DoesNotExist:
                return Response({'Error': 'This Email is not registerd with our platform. kindly verify, If you are actually registered using this Email Id or not?'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Email is required field.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    def post(self, request):
        password_hash = request.data.get('password-hash')
        password = request.data.get('password')
        print(password_hash)

        if password_hash is not None and password is not None:
            try:
                reset_password_instance = PasswordReset.objects.get(password_hash=password_hash, is_active=True)
                reset_password_instance.is_active = False
                reset_password_instance.reset_request_successful = timezone.now()
                reset_password_instance.save()
                reset_password_instance.user.password = make_password(password)
                reset_password_instance.user.save()
                return Response({'success': 'Password changed successfully!'}, status=status.HTTP_200_OK)
            except PasswordReset.DoesNotExist:
                return Response({'error': 'The hash you submitted either does not exist or has expired'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Password Hash and Password is required'}, status=status.HTTP_400_BAD_REQUEST)


class UserAccountDashboardModelViewSet(ModelViewSet):
    """
    Admin side View
    """
    queryset = StudentDetail.objects.all()
    serializer_class = UserAccountDashboardModelSerializer
    permission_classes = [IsAuthenticated, ]
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


class CopyModule(APIView):
    def post(self, request, id):
        if id is not None:
            try:
                module_to_be_cloned =  Module.objects.get(id=id)
                module_to_be_cloned.pk = None
                module_to_be_cloned.save()
                serialized_data = ModuleModelSerializer(module_to_be_cloned)
                return Response(serialized_data.data, status=status.HTTP_201_CREATED)
            except Module.DoesNotExist:
                return Response({'error': 'Module with this ID does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Module ID is required'}, status=status.HTTP_400_BAD_REQUEST)


class SetStartAndCompleteDateInTaskProgressStatus(APIView):
    def post(self, request):
        set_start = request.POST.get('set_start')
        set_complete = request.POST.get('set_complete')
        restart = request.POST.get('restart')
        task_id = request.POST.get('task')


        if set_start and task_id:
            start_time = timezone.now()
            try:
                task = Task.objects.get(id=task_id)
                completed_task = TaskProgressStatus.objects.create(task=task, date_started=start_time, student=request.user)
                serialized_data = TaskProgressStatusModelSerializer(completed_task)
                return Response(serialized_data.data, status=status.HTTP_201_CREATED)
            except Task.DoesNotExist:
                return Response({'error': 'Task Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
        elif set_complete and task_id:
            complete_time = timezone.now()
            try:
                task = Task.objects.get(id=task_id)
                complete_task = TaskProgressStatus.objects.get(task=task)
                complete_task.date_completed = complete_time
                complete_task.save()
                serialized_data = TaskProgressStatusModelSerializer(complete_task)
                return Response(serialized_data.data, status=status.HTTP_200_OK)
            except Task.DoesNotExist:
                return Response({'error': 'Task Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
        if restart and task_id:
            new_start_time = timezone.now()
            try:
                task = Task.objects.get(id=task_id)
                complete_task = TaskProgressStatus.objects.get(task=task)
                complete_task.date_started = new_start_time
                complete_task.date_completed = None
                complete_task.save()
                serialized_data = TaskProgressStatusModelSerializer(complete_task)
                return Response(serialized_data.data, status=status.HTTP_200_OK)
            except Task.DoesNotExist:
                return Response({'error': 'Task Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'set_start or set_complete flag needs to be set along with a Task ID'}, status=status.HTTP_400_BAD_REQUEST)


class ResourceModelViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceModelSerializer
    permission_classes = [IsAuthenticated,]


class EnrollmentFeedbackModelViewSet(ModelViewSet):
    serializer_class = EnrollmentFeedbackModelSerializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        if self.request.method == 'GET':
            if self.request.query_params.get('moduleID', None) and self.request.query_params.get('studentID', None):
                return EnrollmentFeedback.objects.filter(enrollment__in=Enrollment.objects.filter(module_id=self.request.query_params.get('moduleID', None),
                                                                                                  student_id=self.request.query_params.get('studentID', None)), enrollment_status="COM")
            else:
                return EnrollmentFeedback.objects.all()
        else:
            return EnrollmentFeedback.objects.all()


class ReviewModulesTableModelViewSet(ModelViewSet):
    serializer_class = EnrollmentModelSerializer
    pemission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_student:
            if self.request.query_params.get('userID', None):
                return Enrollment.objects.filter(student__id=self.request.query_params.get('userID', None), enrollment_status="IN-REVIEW",
                                                 module__in=StaffDetail.objects.filter(user__id=self.request.user.id).values_list('assigned_modules', flat=True))
            else:
                return Enrollment.objects.none()
        else:
            return Enrollment.objects.none()


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

class StaffToStudentRelationModelViewSet(ModelViewSet):
    serializer_class = CustomStudentDetailModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_student:
            if StaffDetail.objects.filter(user_id=user.id, assigned_modules__isnull=False).exists():
                moduleIDs = StaffDetail.objects.filter(user_id=user.id).values_list('assigned_modules', flat=True)
                if Enrollment.objects.filter(module__id__in=moduleIDs, student__id__isnull=False).exists():
                    userIDs =  Enrollment.objects.filter(module__id__in=moduleIDs, enrollment_status="IN-REVIEW").values_list('student__id', flat=True)
                    return StudentDetail.objects.filter(user__in=userIDs)
                else:
                    return StudentDetail.objects.none()
            else:
                return StudentDetail.objects.none()
        else:
            return StudentDetail.objects.none()


class RejectTask(ModelViewSet):
    queryset = TaskProgressStatus.objects.none()
    permisssion_classes = [IsAuthenticated, ]
    serializer_class = TaskProgressStatusModelSerializer
    
    def partial_update(self, request, pk):
        try:
            instance = TaskProgressStatus.objects.get(id=pk)
            instance.rejected_count += 1
            instance.rejected_feedback = request.data.get('feedback')
            instance.save()
            if QuizAnswer.objects.filter(task_progress_status=pk).exists():
                objs = QuizAnswer.objects.filter(task_progress_status=pk)
                for i in range(len(objs)):
                    objs[i].rejected_count = 1
                QuizAnswer.objects.bulk_update(objs,['rejected_count'])
            return Response({'success': 'Task Rejected Successfully'}, status=status.HTTP_200_OK)
        except TaskProgressStatus.DoesNotExist:
            return Response({'error': 'Invalid Id'}, status=status.HTTP_400_BAD_REQUEST)


class StudentsDetailByResourceModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,]
    serializer_class = StudentsDetailByResourceSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.query_params.get('assign', None):
                students = Resource.objects.filter(id=self.request.query_params.get('resourceID', None)).values_list('users', flat=True)
                if students[0]:
                    return StudentDetail.objects.exclude(user_id__in=students)
                else:
                    return StudentDetail.objects.all()
            else:
                if self.request.query_params.get('resourceID', None):
                    return StudentDetail.objects.filter(user_id__in=Resource.objects.filter(id=self.request.query_params.get('resourceID', None)).values_list('users', flat=True))
                else:
                    return StudentDetail.objects.none()
        else:
            return StudentDetail.objects.none()

class UnAssignResourceModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ResourceModelSerializer
    queryset = Resource.objects.none()

    def partial_update(self, request, pk):
        try:
            instance = Resource.objects.get(id=pk)
            studentID = self.request.data['student']
            instance.users.remove(studentID)
            instance.save()
            return Response({'success': 'Student has been Un-assigned.'}, status=status.HTTP_200_OK)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource Does Not Exists.'}, status=status.HTTP_400_BAD_REQUEST)

class AssignResourceModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ResourceModelSerializer
    queryset = Resource.objects.none()

    def partial_update(self, request, pk):
        try:
            instance = Resource.objects.get(id=pk)
            studentID = self.request.data['student']
            instance.users.add(studentID)
            instance.save()
            return Response({'success': 'Student has been assigned.'}, status=status.HTTP_200_OK)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource Does Not Exists.'}, status=status.HTTP_400_BAD_REQUEST)

class QuizResponseModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = QuizResponseSerializer
    queryset = QuizAnswer.objects.all()
    http_method_names = ['get', 'option', 'head']

    def get_queryset(self):
        if self.request.query_params.get('taskprogressID', None):
            return QuizAnswer.objects.filter(task_progress_status=self.request.query_params.get('taskprogressID', None))
        else:
            return QuizAnswer.objects.none()

class CheckAnswerModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = QuizQuestionOptionModelSerializer
    queryset = QuizQuestionOption.objects.all()
    http_method_names = ['get', 'option', 'head']

    
    def list(self, request):
        question_id = request.query_params.get('question', None)
        question_response = request.query_params.get('options', None)

        if question_response is not None and question_id is not None:
            responses = json.loads(question_response)
            correct_response_count = self.queryset.filter(id__in=responses, question=question_id, weightage__gt=0).count()
            correct_answers_count = self.queryset.filter(question=question_id, weightage__gt=0).count()
            
            if correct_answers_count == correct_response_count:
                return Response({'remark': 'Congratulations your answer was correct.'}, status=status.HTTP_200_OK)
            elif correct_response_count == 0:
                return Response({'remark': 'Your Answers were wrong.'}, status=status.HTTP_200_OK)
            else:
                return Response({'remark': 'Only '+str(correct_response_count)+' ticked option were correct.'}, status=status.HTTP_200_OK)
        else:
            return Response({'remark': 'No answers found.'}, status=status.HTTP_200_OK)


class CustomDeleteModuleModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,]
    serilaizer_class = ModuleModelSerializer
    queryset = Module.objects.all()
    http_method_names = ['delete', 'option', 'head']

    
    def destroy(self, request, pk):
        try:
            instance = Module.objects.get(id=pk)
            if Enrollment.objects.filter(module__id=instance.id, enrollment_status='IN-PROGRESS').exists():
                return Response({'Module': 'Module with In-Progress Enrollment cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            elif Enrollment.objects.filter(module__id=instance.id, enrollment_status='IN-REVIEW').exists():
                return Response({'Module': 'Module with In-Review Enrollment cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            elif Enrollment.objects.filter(module__id=instance.id, enrollment_status='RE-SUBMIT').exists():
                return Response({'Module': 'Module with Re-submit Enrollment cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                instance.delete()
                return Response({'Module': 'Module has been deleted'}, status=status.HTTP_200_OK)
        except Module.DoesNotExist:
            return Response({'error': 'Object Not Found'}, status=status.HTTP_404_OK)
