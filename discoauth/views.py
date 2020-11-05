# -*- coding:utf-8 -*-

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import (authenticate, login, logout)
from django.contrib import messages
from django.core.exceptions import PermissionDenied


class LoginView(View):
    """
    View used to provide the complete
    login functionality for this application
    for for the students and teachers.
    """
    
    template_name = "discoauth/login.html"

    def get(self, request):
        """
        Method used to return the template
        of the Login view when a get request
        is provided to this View. If the user
        is authenticated, It will automatically
        redirect it to the descired View based
        on the fact if user is  teacher or student.
        """
        if request.user.is_authenticated:
            if request.user.is_teacher:
                return redirect('portal:dashboard')
            elif request.user.is_student:
                return redirect('portal:student-dashboard')
            elif request.user.is_staff:
                return redirect('portal:staff-dashboard')
            else:
                raise PermissionDenied("Your account don't have sufficient permissions")
        else:
            return render(request, self.template_name)


    def post(self, request):
        """
        Method used to receive the POST
        request with user login credentials
        from Login Form. If everything is validated
        user is redirected to His/Her dashboard.
        other wise a validation error will displayed
        on the Login Page.
        """
        user = authenticate(email=request.POST.get("email", None),
                            password=request.POST.get("password", None))
        if user is not None:
            login(request, user)
            if user.is_teacher:
                return redirect('portal:dashboard')
            elif user.is_student:
                return redirect('portal:student-dashboard')
            elif user.is_staff:
                return redirect('portal:staff-dashboard')
            else:
                raise PermissionDenied("Your account don't have sufficient permissions")
        else:
            messages.error(
                request, "Email or Password entered is incorrect", extra_tags='alert-danger')
            return redirect('discoauth:login')


class LogoutView(View):
    """
    View class used to provide the logout
    functionality. By acceptiong the logout request
    and redirecting the user to loging page.
    """
    def get(self, request):
        logout(request)
        return redirect('discoauth:login')



class ForgotPasswordView(View):
    """
    View Used to Provide the forgot
    password functionality, It will only
    receive get request and provide the forgot
    password HTML page for user to enter the user
    account details. Every thing else will be done
    using REST API application named 'api' in this project.
    """
    template_name = 'discoauth/forgot-password.html'

    def get(self, request):
        """
        Method used to render the forgot password template
        on a GET request to the forogot password endpoint.
        """
        return render(request, self.template_name)
