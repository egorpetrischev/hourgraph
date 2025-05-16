from django.test import TestCase
from hourgraph.models import Users, StudentCard

class StudentCardModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем пользователя и студенческую карточку для тестов
        cls.user = Users.objects.create(username='testuser', name='Test User')
        cls.student_card = StudentCard.objects.create(
            user=cls.user,
            name='John',
            surname='Doe',
            contacts='1234567890',
            comment='Test comment',
            address='Test address',
            lesson_price=100.00
        )

    def student_card_creation(self):
        """Проверяем, что студенческая карточка создана корректно."""
        self.assertEqual(self.student_card.name, 'John')
        self.assertEqual(self.student_card.surname, 'Doe')
        self.assertEqual(self.student_card.contacts, '1234567890')
        self.assertEqual(self.student_card.comment, 'Test comment')
        self.assertEqual(self.student_card.address, 'Test address')
        self.assertEqual(self.student_card.lesson_price, 100.00)

    def test_student_card_str_method(self):
        """Проверяем метод __str__."""
        self.assertEqual(str(self.student_card), 'John Doe')