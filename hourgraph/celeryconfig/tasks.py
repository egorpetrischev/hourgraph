import os
import django
from celery import shared_task
from django.utils import timezone


timezone.activate('Europe/Moscow')  # Явно активируем нужный пояс

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


@shared_task
def check_lesson_status():
    from hourgraph.models import Lesson  # Импорт модели
    now = timezone.localtime(timezone.now())
    current_date = now.date()
    current_time = now.time()
    print(current_time)

    lessons = Lesson.objects.filter(
        date__lt=current_date,  # Уроки, дата которых раньше сегодня
        status='TB'
    ) | Lesson.objects.filter(
        date=current_date,  # ИЛИ уроки сегодня, но время окончания прошло
        end_time__lte=current_time,
        status='TB'
    )

    updated_count = lessons.update(status='CO')
    return f"Updated {updated_count} lessons"