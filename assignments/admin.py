# -*- coding: utf-8 -*-

from django.contrib import admin
from assignments.models import *

class ModuleCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    fields = ['category_type', 'category_description', 'created_at', 'updated_at']


class TaskAdmin(admin.ModelAdmin):
    raw_id_fields = ['lesson']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['task_name', 'task_description', 'duration', 'content_type',
              'response_type', 'lesson', 'task_file', 'created_at', 'updated_at']


class ModuleLessonAdmin(admin.ModelAdmin):
    raw_id_fields = ['module']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['lesson_name', 'module', 'completed', 'created_at', 'updated_at']


class ModuleAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    fields = ['title', 'short_title', 'description', 'module_category',
              'status', 'cover_image', 'created_at', 'updated_at']

class ModuleStatusAdmin(admin.ModelAdmin):
    fields = ['description']


class EnrollmentAdmin(admin.ModelAdmin):
    raw_id_fields = ['module']
    fields = ['student', 'module', 'enrollment_status', 'enrollment_method', 'total_tasks',
              'tasks_completed', 'date_set', 'date_to_start', 'date_due', 'date_completed', "rejected_count"]
    readonly_fields = ['total_tasks', 'tasks_completed', 'date_set']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = DiscoUser.objects.filter(is_student=True)
        return super(EnrollmentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class StudentDetailAdmin(admin.ModelAdmin):
    fields = ['user', 'roll_number', 'student_type']


class ResourceAdmin(admin.ModelAdmin):
    fields = ['users','resource_title', 'resource_short_title', 'resource_description', 'suggested_student_type', 'file_type', 'can_be_downloaded', 'resource_cover_image', 'resource_text',
              'resource_media_file', 'created', 'updated']
    readonly_fields = ['created', 'updated']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "users":
            kwargs["queryset"] = DiscoUser.objects.filter(is_student=True)
        return super(ResourceAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class EnrollmentFeedbackAdmin(admin.ModelAdmin):
    raw_id_fields = ['enrollment']
    fields = ['enrollment','enrollment_status', 'comment', 'feedback_file']


class StaffDetailAdmin(admin.ModelAdmin):
    raw_id_fileds = ['assigned_modules', ]
    fields = ['staff_id', 'user','assigned_modules', 'staff_role']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = DiscoUser.objects.filter(is_teacher=True)
        return super(StaffDetailAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TaskProgressStatusAdmin(admin.ModelAdmin):
    readonly_fields = ['task', 'date_started', 'date_completed', 'task_response_file', 'task_response_text', 'rejected_count']
    fields = ['enrollment', 'task', 'date_started', 'date_completed', 'task_response_file', 'task_response_text', 'rejected_count', "enrollment_updated"]


admin.site.register(ModuleCategory, ModuleCategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(ModuleLesson, ModuleLessonAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(QuizQuestionOption)
admin.site.register(QuizQuestion)
admin.site.register(QuizAnswer)
admin.site.register(StudentDetail, StudentDetailAdmin)
admin.site.register(Resource, ResourceAdmin)
#admin.site.register(ResourceData)
admin.site.register(EnrollmentFeedback, EnrollmentFeedbackAdmin)
admin.site.register(StaffDetail, StaffDetailAdmin)
admin.site.register(TaskProgressStatus, TaskProgressStatusAdmin)
