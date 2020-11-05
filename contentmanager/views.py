# -*- coding: utf-8 -*-

from django.shortcuts import render
from discoauth.models import DiscoUser
from django.views import View
from assignments.models import ModuleCategory, ModuleLesson, Task, StaffDetail
from django.http import Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from assignments.models import Module
from django.core.exceptions import PermissionDenied


def get_staff_role(id):
    try:
        staff_detail = StaffDetail.objects.get(user__id=id)
        return staff_detail.staff_role
    except StaffDetail.DoesNotExist:
        return None


class HomeContentManager(LoginRequiredMixin, View):
    template_name = 'content-manager/content-manager-home.html'

    def get(self, request):
        staff_role = get_staff_role(self.request.user.id)
        if staff_role == "MAN" or staff_role == "CC":
            return render(request, self.template_name, context={'title': 'Content Manager'})
        else:
            raise PermissionDenied("Only Managers and Content Creators are allowed to access this page")


class CreateModule(LoginRequiredMixin, View):
    template_name = 'content-manager/create-module.html'

    def get(self, request):
        staff_role = get_staff_role(self.request.user.id)
        if staff_role == "MAN" or staff_role == "CC":
            return render(request, self.template_name, context={'module_categories': ModuleCategory.objects.all(), 'title': 'Create Module' })
        else:
            raise PermissionDenied("Only Managers and Content Creators are allowed to access this page")


class EditModule(LoginRequiredMixin, View):
    template_name = 'content-manager/edit-module.html'

    def get(self, request, id):
        if id is not None:
            staff_role = get_staff_role(self.request.user.id)
            if request.user.is_admin or staff_role == "MAN" or staff_role == "CC":
                try:
                    module = Module.objects.get(id=id)
                    categories = ModuleCategory.objects.all()
                    lessons = ModuleLesson.objects.filter(module=module)
                    return render(request, self.template_name, context={'module': module, 'lessons': lessons, 'categories': categories, 'title': 'Edit Module'})
                except Module.DoesNotExist:
                    raise Http404("Module does not exists")
            return PermissionDenied("You dont have permission to access this page")
        else:
            raise Http404("No Module Found with using lookup %s" % (id))


class CreateQuiz(LoginRequiredMixin, View):
    template_name = "content-manager/create-quiz.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={'title': 'Create Quiz'})


class EditQuiz(LoginRequiredMixin, View):
    template_name = "content-manager/edit-quiz.html"

    def get(self, request, pk, *args, **kwargs):
        try:
            Quiz = Quiz.objects.get(id=pk)
            return render(request, self.template_name, {'quiz': quiz})
        except Quiz.DoesNotExist:
            raise Http404("Quiz you are looking for Does Not Exist")


class AddEditQuizQuestionsView(LoginRequiredMixin, View):
    template_name = "content-manager/add-edit-quiz-questions.html"
    
    def get(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(id=pk)
            return render(request, self.template_name, context={"quiz": task, "questions": task.questions.all(), 'title': 'Add/Edit Quiz'})
        except Task.DoesNotExist:
            raise Http404("TaskQuiz with ID %s Does Not Exist" %(Task))
                                    
