from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):  # Таблица "Users"
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class StudentCard(models.Model):    # Таблица "Student_card"
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    surname = models.CharField(max_length=256, null=True, blank=True)
    contacts = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    lesson_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.name}' if not self.surname else f'{self.name} {self.surname}'


class StudentCardGroup(models.Model):   # Таблица "Student_card_group"
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    students = models.ManyToManyField(StudentCard)
    name = models.CharField(max_length=256)
    comment = models.TextField(null=True, blank=True)
    lesson_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class LessonTemplate(models.Model): # Таблица "Lesson_template"
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    students = models.ManyToManyField(StudentCard)
    student_group = models.ForeignKey(StudentCardGroup, on_delete=models.SET_NULL, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    weekday = models.CharField(max_length=2, default='MO', choices=(
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ))
    comment = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.weekday} {self.start_time}-{self.end_time}'


class Lesson(models.Model): # Таблица "Lesson"
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    students = models.ManyToManyField(StudentCard)
    student_group = models.ForeignKey(StudentCardGroup, on_delete=models.SET_NULL, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    status = models.CharField(max_length=2, default='TB', choices=(
        ('TB', 'To be'),
        ('PR', 'Processing'),
        ('CO', 'Completed')
    ))
    comment = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.date} {self.start_time}-{self.end_time}'
