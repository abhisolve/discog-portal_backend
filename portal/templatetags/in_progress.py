# -*- coding: utf-8 -*-

from django import template
from assignments.models import TaskProgressStatus, QuizAnswer

register = template.Library()

@register.filter(name="is_started")
def is_started(task, enrollment):
    try:
        TaskProgressStatus.objects.get(task=task,
                                       enrollment=enrollment,
                                       date_started__isnull=False,
                                       date_completed__isnull=True)
        return True
    except TaskProgressStatus.DoesNotExist:
        return False


@register.filter(name="task_progress_status_id")
def task_progress_status_id(task, enrollment):
    try:
        return TaskProgressStatus.objects.get(task=task,
                                       enrollment=enrollment,
                                       date_started__isnull=False,
                                       date_completed__isnull=True).id
    except TaskProgressStatus.DoesNotExist:
        return None

@register.filter(name="question_attempt_exist")
def question_attempt_exist(question, enrollment):
    """
    filter used to check if the attempt for the question exists
    in the database and return True or Fasle based on this condition
    """
    
    if QuizAnswer.objects.filter(question__id=question.id, user__id=enrollment.student.id, rejected_count=0).exists():
        print("Returning True")
        return True
    else:
        print("Returning False")
        return False
    
@register.filter(name="rejected_task_feedback")
def rejected_task_feedback(task, enrollment):
    """
    used to return rejected feedback of any rejected_current_task.
    """
    try:
        return TaskProgressStatus.objects.filter(task=task,
                                                 enrollment=enrollment,
                                                 rejected_count=1).last().rejected_feedback
    except TaskProgressStatus.DoesNotExist:
        return None
