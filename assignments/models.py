#-*- coding: utf-8 -*-

from django.db import models
from ckeditor.fields import RichTextField
from discoauth.models import DiscoUser
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.utils import timezone


def _update_filename(instance, filename):
    extension = filename.split('.')[-1]
    return f"task_media_files/{instance.task_name}/{get_random_string(32)+'.'+extension}"


class ModuleCategory(models.Model):
    """
    Each module will have a category it is like labels
    that will be used to uniqely identify the modules of
    a particular category
    """
    category_type = models.CharField(max_length=255, unique=True)
    category_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module Category"
        verbose_name_plural = "Module Categories"

    def __str__(self):
        return self.category_type


class Task(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('TXT', 'RICH TEXT'),
        ('IMG', 'IMAGE'),
        ('TXT-IMG', 'TEXT AND IMAGE'),
        ('PDF', 'PDF'),
        ('VIDEO', 'VIDEO'),
        ('QUIZ', 'QUIZ'),
        ('FILE', 'UPLOAD FILE - DOWNLOAD FILE'),
        ('INPUT-FIELD', 'INPUT FIELD'),
    ]
    RESPONSE_TYPE_CHOICES = [
        ('NONE', 'NONE'),
        ('TXT', 'RICH TEXT'),
        ('FILE', 'FILE'),
        ('QUIZ', 'QUIZ')
    ]
    task_name = models.CharField(max_length=255)
    task_description = RichTextField(null=True, blank=True)
    lesson = models.ForeignKey('modulelesson', on_delete=models.CASCADE, related_name='tasks')
    duration = models.TimeField(null=True, blank=True)
    content_type = models.CharField(choices=CONTENT_TYPE_CHOICES, max_length=30, default='TXT')
    response_type = models.CharField(choices=RESPONSE_TYPE_CHOICES, max_length=30, default='NONE')
    task_file = models.FileField(upload_to=_update_filename, null=True, blank=True, max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.task_name

    def clean(self):
        super(Task, self).clean()
        
        if self.content_type == 'TXT' and not self.task_description:
            raise ValidationError({'task_description': 'Task description is required for task with content type text'})
        elif self.content_type == 'IMG' and not self.task_file:
            raise ValidationError({'task_file': 'Task file is required for task with content type Image'})
        elif self.content_type == 'TXT-IMG':
            if not self.task_description and not self.task_file:
                raise ValidationError({'task_description': 'Task description is required for task with content type Text & Image',
                                       'task_file': 'Task file is required for task with content type Text & Image'})
            elif not self.task_description:
                raise ValidationError({'task_description': 'Task description is required for task with content type Text & Image'})
            elif not self.task_file:
                raise ValidationError({'task_file': 'Task file is required for task with content type Text & Image'})
            else:
                pass
        else:
            pass


class QuizQuestion(models.Model):
    """
    Each Quiz will have questions in it
    This question will be stored in this model
    """
    QUESTION_TYPE_CHOICES = [
        ('MC', 'Multiple Choice'),
        ('SC', 'Single Choice'),    ]
    question = models.TextField()
    question_type = models.CharField(choices=QUESTION_TYPE_CHOICES, max_length=2, default='MC')
    quiz_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="questions")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "#%s - Quiz(#%s) - Type(%s)" % (self.id, self.quiz_task.id, self.question_type)


    def clean(self):
        super(QuizQuestion, self).clean()
        if self.quiz_task.content_type != "QUIZ":
            raise ValidationError({"quiz_task": "Quiz Task is not of type Quiz"})
        else:
            pass


    class Meta:
        verbose_name = 'Quiz Question'
        verbose_name_plural = 'Quiz Questions'


class ModuleLesson(models.Model):
    lesson_name = models.CharField(max_length=255)
    module = models.ForeignKey('module', on_delete=models.CASCADE, related_name="lessons")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module Lesson"
        verbose_name_plural = "Module Lessons"

    def __str__(self):
        return self.lesson_name


class Module(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
    ]
    title = models.CharField(max_length=255)
    description = RichTextField()
    module_category = models.ForeignKey(ModuleCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='modules')
    status = models.CharField(choices=STATUS_CHOICES,null=True, blank=True, max_length=255, default="DRAFT")
    short_title = models.CharField(max_length=255, null=True, blank=True)
    cover_image = models.FileField(upload_to='module-cover-image', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return self.title

    @property
    def get_enrolled_student_count(self):
        return Enrollment.objects.filter(module=self).count()
    
    def clean(self):
        super(Module, self).clean()
        if self.status == "PUBLISHED":
            if not  Task.objects.filter(lesson__module=self.id).count() > 0:
                raise ValidationError({'status': "Module cannot be published. Please add tasks to publish the module."})
            elif Task.objects.filter(lesson__module=self.id, content_type = 'QUIZ').exists():
                quiz_tasks = Task.objects.filter(lesson__module=self.id, content_type = 'QUIZ')
                quiz_questions = QuizQuestion.objects.filter(quiz_task__in=quiz_tasks)
                if quiz_tasks.count() != quiz_questions.distinct('quiz_task').count():
                    raise ValidationError({'status': "Module cannot be published. Please add atleast one question in every quiz type task."})
                elif QuizQuestionOption.objects.filter(question__in=quiz_questions).distinct('question').count() != quiz_questions.count():
                    raise ValidationError({'status': "Module cannot be published. Please add atleast one option in every quiz question."})
            else:
                pass


class Enrollment(models.Model):
    Status_choices = [
        ('NOT-STARTED', 'NOT STARTED'),
        ('IN-REVIEW','IN REVIEW'),
        ('RE-SUBMIT','RE SUBMIT'),
        ('IN-PROGRESS', 'IN PROGRESS'),
        ('COMPLETED', 'COMPLETED'),
        ('NEXT-MODULE', 'NEXT MODULE'),
    ]
    Method_choices = [
        ('AUTOMATIC', 'AUTOMATIC ENROLLMENT'),
        ('MANUAL', 'MANUAL ENROLLMENT'),
        ('SETDATE', 'SET DATE'),
    ]
    student = models.ForeignKey(DiscoUser, on_delete=models.CASCADE, related_name='enrollments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_status = models.CharField(choices=Status_choices, max_length=30, default=None)
    enrollment_method = models.CharField(choices=Method_choices, max_length=30, default=None)
    total_tasks = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    rejected_count = models.PositiveIntegerField(blank=False, default=0)
    date_set = models.DateTimeField(null=True, blank=True)
    date_to_start = models.DateTimeField(null=True, blank=True)
    date_due = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    def clean(self):
        super(Enrollment, self).clean()
        if self.module.status == "DRAFT":
            raise ValidationError({'module': "Enrollment can only be created for Published Modules."})
        if self.total_tasks < self.tasks_completed:
            raise ValidationError({'tasks_completed': "Tasks completed can't be more than total tasks"})
        #if self.total_tasks != self.tasks_completed and self.enrollment_status == "IN-REVIEW":
            #raise ValidationError({'enrollment_status': "Enrollment can only be In review status when total tasks is equal to task completed."})
        #if self.total_tasks != self.tasks_completed and self.enrollment_status == "COMPLETED":
            #raise ValidationError({'enrollment_status': "Enrollment can only be Completed status when total tasks is equal to task completed."})
        
    def __str__(self):
        return "#%s %s" % (self.id, self.module.title)

    @property
    def tasks(self):
        return Task.objects.filter(lesson__module__id=self.module.id).order_by('created_at')

    @property
    def not_started_tasks(self):
        """
        return the task whose task progress exists
        but it is not marked as started by the user
        """
        tasks = self.tasks.exclude(id__in=self.task_progress.values_list('task_id', flat=True))
        if tasks.exists():
            return tasks
        else:
            return None

    @property
    def task_started_but_not_completed(self):
        """
        return the task progress which is started but not
        completed
        """
        task_progress = self.task_progress.filter(date_completed__isnull=True, rejected_count=self.rejected_count)
        if task_progress.exists():
            return task_progress.first().task
        else:
            return None
            
    @property
    def not_started_rejected_task(self):
        rejected_tasks = self.task_progress.filter(rejected_count=self.rejected_count).values_list('task_id', flat=True)
        started_task_progress = self.task_progress.filter(task_id__in=rejected_tasks, rejected_count='0').values_list('task_id', flat=True)
        task_progress = self.task_progress.filter(task_id__in=rejected_tasks).exclude(task_id__in=started_task_progress)
        if task_progress.exists():
            return task_progress.first().task
        else:
            return None
        
    @property
    def rejected_task_started_but_not_completed(self):
        rejected_tasks = self.task_progress.filter(rejected_count=self.rejected_count).values_list('task_id', flat=True)
        task_progress = self.task_progress.filter(task_id__in=rejected_tasks, rejected_count=0, date_completed__isnull=True)
        if task_progress.exists():
            return task_progress.first().task
        else:
            return None
        
    @property
    def current_task(self):
        """
        This is the task which should be assigned to
        the student if he just go the in-progress-module
        page in student dashboard.
        """
        if self.rejected_count == 0:
            if not self.task_progress.exists():
                # when task progress doesn't exist
                return Task.objects.filter(lesson__module=self.module).first()
            elif self.task_started_but_not_completed is not None:
                return self.task_started_but_not_completed
            elif self.not_started_tasks is not None:
                return self.not_started_tasks.first()
            else:
                return None
        else:
            if self.rejected_task_started_but_not_completed is not None:
                return self.rejected_task_started_but_not_completed
            elif self.not_started_rejected_task is not None:
                return self.not_started_rejected_task
            else:
                return None
                                                                                                                                                        
    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollements'
        unique_together = ['student', 'module']


class TaskProgressStatus(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name="task_progress", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='task_progress_statuses', on_delete=models.CASCADE)
    enrollment_updated = models.BooleanField(default=False)
    task_response_text = RichTextField(null=True, blank=True)
    task_response_file = models.FileField(upload_to='task-response-files/', null=True, blank=True)
    rejected_count = models.PositiveIntegerField(blank=False, default=0)
    rejected_feedback = models.CharField(max_length=255, null=True, blank=True)
    date_started = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.enrollment.student.first_name, self.task.task_name)

    class Meta:
        verbose_name = 'Task Progress Status'
        verbose_name_plural = 'Task Progress status'
        
    def clean(self):
        super(TaskProgressStatus, self).clean()
        if self.task.response_type == "FILE" and not self.task_response_file and self.date_completed:
            raise ValidationError({'date_completed': "Date completed cannot be set without a response file"})
        if self.task.response_type == "TXT" and not self.task_response_text and self.date_completed:
            raise ValidationError({'date_completed': "Date completed cannot be set without a response text"})


class StudentDetail(models.Model):
    user = models.OneToOneField(DiscoUser, null=True, blank=True, on_delete=models.CASCADE, related_name='student_detail')
    roll_number = models.CharField(max_length=255)
    student_type = models.CharField(max_length=20)

    def __str__(self):
        return self.user.email

    def clean(self):
        super(StudentDetail, self).clean()
        if not self.user.is_student:
            raise ValidationError({'user': "User should of type student"})

    @property
    def sibling_number(self):
        sibling_number = 1
        parent = self.user.parent
        childrens = parent.childrens.order_by('id')
        for children in childrens:
            if children == self.user:
                return sibling_number
            else:
                sibling_number += 1

    class Meta:
        verbose_name = 'Student Detail'
        verbose_name_plural = 'Student Details'


class Resource(models.Model):
    content_type = [
        ('TXT', 'TEXT'),
        ('IMG', 'IMAGE'),
        ('PDF', 'PDF'),
    ]
    users = models.ManyToManyField(DiscoUser, related_name='resources')
    resource_title = models.CharField(max_length=255)
    resource_short_title = models.CharField(max_length=20, blank=True, null=True)
    resource_description = RichTextField()
    suggested_student_type = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(choices=content_type, max_length=255, default='PDF')
    can_be_downloaded = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    resource_cover_image = models.FileField(upload_to='resource-cover-image/')
    resource_text = RichTextField(null=True, blank=True)
    resource_media_file = models.FileField(upload_to='resource-media-files/', null=True, blank=True)

    def __str__(self):
        return self.resource_title

    def clean(self):
        super(Resource, self).clean()
        if self.file_type == 'TXT' and not self.resource_text and self.resource_media_file:
            raise ValidationError({'resource_text': "Please enter your Resource.", 'resource_media_file': "Invalid Input: Leave it Blank for Text type Resource."})
        if self.file_type == 'TXT' and not self.resource_text:
            raise ValidationError({'resource_text': "**Required Field for Text type Resource."})
        if self.file_type != 'TXT' and self.resource_text and not self.resource_media_file:
            raise ValidationError({'resource_text': "Invalid Input: Leave it Blank for Non-Text type Resource."})
        if self.file_type !='TXT' and not self.resource_media_file:
            raise ValidationError({'resource_text': "**Required Field."})
        
    class Meta:
        verbose_name = "Resource"
        verbose_name_plural = "Resources"


class EnrollmentFeedback(models.Model):
    FEEDBACK_CHOICES = (('COM', 'COMPLETED'),
                        ('RES', 'RE-SUBMIT'))
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_status = models.CharField(max_length=10,choices=FEEDBACK_CHOICES)
    comment = RichTextField()
    feedback_file = models.FileField(upload_to='feedback-documents/', blank=True)

    def __str__(self):
        return "%#s - %s" % (self.enrollment.id, self.enrollment.student.first_name)

    def clean(self):
        super(EnrollmentFeedback,self).clean()
        if EnrollmentFeedback.objects.filter(enrollment_status="COM", enrollment=self.enrollment).exists():
            raise ValidationError({'enrollment': "Completed enrollment can only have single feedback"})
        
    class Meta:
        verbose_name = 'Enrollment Feedback'
        verbose_name_plural = 'Enrollment Feedbacks'


class StaffDetail(models.Model):
    STAFF_ROLE_CHOICES = (('MAN', 'Manager'),
                          ('CC', 'Content Creator'),
                          ('MOD', 'Moderator'))
    staff_id = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(DiscoUser, related_name="staff_detail", on_delete=models.CASCADE)
    staff_role = models.CharField(max_length=3, choices=STAFF_ROLE_CHOICES)
    assigned_modules = models.ManyToManyField(Module, related_name="staff_details", null=True, blank=True)

    def __str__(self):
        return "%#s - %s - %s" % (self.id, self.staff_role, self.user.email)

    class Meta:
        verbose_name = "Staff Detail"
        verbose_name_plural = "Staff Details"


class QuizQuestionOption(models.Model):
    """
    Each Quiz Question will have Options associated with it
    This models is used to store the Option of the Quiz Question
    With an indicator if it is correct or not and the weightage of
    of the option.
    """
    question = models.ForeignKey(QuizQuestion, related_name="options", on_delete=models.CASCADE)
    option_content = models.TextField()
    weightage = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "#%s - Question(#%s) %s" % (self.id, self.question.id, self.weightage)

    class Meta:
        verbose_name = 'Quiz Question Option'
        verbose_name_plural = 'Quiz Question Options'


class QuizAnswer(models.Model):
    """
    When student will attempt the quiz.
    he will answer the questions in the quiz
    and this models will be used to store the answer
    of the questions in the quiz.
    """
    user = models.ForeignKey(DiscoUser, on_delete=models.CASCADE, related_name='quiz_answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='quiz_answers')
    options = models.ManyToManyField(QuizQuestionOption, related_name='quiz_answers')
    rejected_count = models.IntegerField(default=0)
    task_progress_status = models.ForeignKey(TaskProgressStatus, related_name="quiz_answers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question.question


    class Meta:
        verbose_name = "Quiz Answer"
        verbose_name_plural = "Quiz Answers"


@receiver(post_save, sender=Enrollment, dispatch_uid="enrollment_post_save")
def enrollment_post_save(sender, instance, created, **kwargs):
    """
    Post save tirgger used for updating the values
    in Enrollement model
    """
    
    def check_and_assign_date_completed(instance):
        """
        closure used to check if the task if completed or not.
        if completed updated its enrollment status and date_completed
        """
        if instance.total_tasks != 0:
            if instance.enrollment_status == 'IN-PROGRESS' and instance.total_tasks == instance.tasks_completed:
                Enrollment.objects.filter(id=instance.id).update(date_completed=timezone.now(),
                                                                 enrollment_status="IN-REVIEW")
                # find the next enrollment and update its status
                # to IN-PROGRESS
                if Enrollment.objects.filter(student=instance.student, enrollment_status='RE-SUBMIT').exists():
                    Enrollment.objects.filter(id=Enrollment.objects.filter(enrollment_status='RE-SUBMIT',
                                                                           student=instance.student).first().id).update(enrollment_status='IN-PROGRESS',
                                                                                                                        tasks_completed=TaskProgressStatus.objects.filter(
                                                                                                                        enrollment_id=Enrollment.objects.filter(enrollment_status='RE-SUBMIT',
                                                                                                                                                                student=instance.student).first().id,
                                                                                                                            rejected_count=0).count())
                else:
                    try:
                        next_enrollment = Enrollment.objects.get(student=instance.student,
                                                                 enrollment_status='NEXT-MODULE')
                        next_enrollment.enrollment_status = 'IN-PROGRESS'
                        next_enrollment.save()
                    except Enrollment.DoesNotExist:
                        pass

                    if Enrollment.objects.filter(student=instance.student, enrollment_status='NOT-STARTED').exists():
                        Enrollment.objects.filter(id=Enrollment.objects.filter(enrollment_status='NOT-STARTED',
                                                                               student=instance.student).first().id).update(enrollment_status='NEXT-MODULE')
                    else:
                        pass
                        
            elif not Enrollment.objects.filter(student=instance.student, enrollment_status='IN-PROGRESS').exists() and Enrollment.objects.filter(id=instance.id, enrollment_status='RE-SUBMIT').exists():
                Enrollment.objects.filter(id=instance.id).update(enrollment_status='IN-PROGRESS', tasks_completed=TaskProgressStatus.objects.filter(enrollment_id=instance.id, rejected_count=0).count())
            else:
                pass
        else:
            pass

    if created:
        #autofill the total_tasks in the enrollment
        Enrollment.objects.filter(id=instance.id).update(total_tasks=Task.objects.filter(lesson__module__id=instance.module.id).count())
        # logic to update the enrollment_status
        if Enrollment.objects.filter(student=instance.student).exists():
            if Enrollment.objects.filter(student=instance.student, enrollment_status="NEXT-MODULE").exists():
                Enrollment.objects.filter(id=instance.id).update(enrollment_status='NOT-STARTED')
            elif Enrollment.objects.filter(student=instance.student, enrollment_status="IN-PROGRESS").exists():
                Enrollment.objects.filter(id=instance.id).update(enrollment_status='NEXT-MODULE')
            else:
                Enrollment.objects.filter(id=instance.id).update(enrollment_status='IN-PROGRESS')
        else:
            # No other enrollment exists
            # so update this enrollment to In-Progress
            Enrollment.objects.filter(id=instance.id).update(enrollment_status='IN-PROGRESS')
    else:
        check_and_assign_date_completed(instance)


@receiver(post_save, sender=TaskProgressStatus, dispatch_uid="task_progress_status_post_save")
def task_progress_status_post_save(sender, instance, created, **kwargs):
    try:
        if instance.date_completed and instance.enrollment_updated is False:
            enrollment = instance.enrollment
            enrollment.tasks_completed = enrollment.tasks_completed + 1
            enrollment.save()
            TaskProgressStatus.objects.filter(id=instance.id).update(enrollment_updated=True)
        else:
            pass
    except Enrollment.DoesNotExist:
        pass


@receiver(post_save, sender=Task, dispatch_uid="task_post_save")
def task_post_save(sender, instance, created, **kwargs):
    if created:
        enrollments = Enrollment.objects.filter(module__id=instance.lesson.module.id)
        for i in range(len(enrollments)):
            enrollments[i].total_tasks += 1
        Enrollment.objects.bulk_update(enrollments,['total_tasks'])


@receiver(pre_delete, sender=Task, dispatch_uid="task_pre_delete")
def task_pre_delete(sender, instance, **kwargs):
        enrollments = Enrollment.objects.filter(module__id=instance.lesson.module.id)
        for i in range(len(enrollments)):
            enrollments[i].total_tasks -= 1
        Enrollment.objects.bulk_update(enrollments,['total_tasks'])


@receiver(pre_delete, sender=TaskProgressStatus, dispatch_uid="task_progres_status_pre_delete")
def task_progres_status_pre_delete(sender, instance, **kwargs):
    """
    We need to update the enrollment task_completed count
    also
    """
    try:
        enrollment = instance.enrollment
        if instance.enrollment_updated:
            enrollment.tasks_completed = enrollment.tasks_completed - 1
            enrollment.save()
        else:
            pass
    except Enrollment.DoesNotExist:
        pass

@receiver(post_save, sender=EnrollmentFeedback, dispatch_uid="module_feedback_post_save")
def module_feedback_post_save(sender, instance, created, **kwargs):
    
    #post_save trigger for module_feedback to update enrollment status to completed.
    if created:
        try:
            enrollment = Enrollment.objects.get(id=instance.enrollment.id)
            if instance.enrollment_status == "COM":
                enrollment.enrollment_status = "COMPLETED"
                enrollment.save()
            elif instance.enrollment_status == "RES":
                enrollment.enrollment_status = "RE-SUBMIT"
                enrollment.rejected_count = 1
                enrollment.save()
            else:
                pass
        except Enrollment.DoesNotExist:
            pass
