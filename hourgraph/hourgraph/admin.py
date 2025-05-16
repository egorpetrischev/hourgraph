from django.contrib import admin
from .models import Users, StudentCard, StudentCardGroup, Lesson, LessonTemplate


admin.site.register(Users)
admin.site.register(StudentCard)
admin.site.register(StudentCardGroup)
admin.site.register(Lesson)
admin.site.register(LessonTemplate)
