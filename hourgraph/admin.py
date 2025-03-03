from django.contrib import admin
from .models import Users, StudentCard, StudentCardGroup, Lesson, LessonTemplate


admin.register(Users)
admin.register(StudentCard)
admin.register(StudentCardGroup)
admin.register(Lesson)
admin.register(LessonTemplate)
