from datetime import date, time

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from rest_framework.test import APIClient

from .models import (
    UserProfile,
    Category,
    Tour,
    Booking,
    Review
)


class NomadToursTests(TestCase):

    def setUp(self):
        # Создаём пользователя
        self.user = User.objects.create_user(
            username='ravil',
            password='12345'
        )

        self.other_user = User.objects.create_user(
            username='guest',
            password='12345'
        )

        # Авторизуем пользователя
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Создаём категории
        self.horse = Category.objects.create(name='Конный')
        self.walk = Category.objects.create(name='Пеший')
        self.moto = Category.objects.create(name='Мото')

        # Создаём тур
        self.tour = Tour.objects.create(
            title='Тур по горам',
            description='Путешествие по горам Кыргызстана',
            price=2500
        )

        self.tour.categories.add(self.horse, self.walk)

    # 1. Проверка связи 1:1
    def test_create_profile(self):
        profile = UserProfile.objects.create(
            user=self.user,
            phone='0555123456',
            city='Бишкек'
        )

        self.assertEqual(profile.user, self.user)

    def test_user_cannot_have_two_profiles(self):
        UserProfile.objects.create(
            user=self.user,
            phone='0555123456',
            city='Бишкек'
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserProfile.objects.create(
                    user=self.user,
                    phone='0777123456',
                    city='Ош'
                )

    # 2. Проверка связи M:M
    def test_tour_multiple_categories(self):
        self.assertEqual(self.tour.categories.count(), 2)

        self.tour.categories.add(self.moto)

        self.assertEqual(self.tour.categories.count(), 3)

    # 3. Проверка создания бронирования
    def test_create_booking(self):
        response = self.client.post(
            '/api/bookings/',
            {
                'tour': self.tour.id,
                'date': '2026-12-15',
                'time': '10:00:00'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)

    # 4. Запрет повторного бронирования
    def test_duplicate_booking(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            date=date(2026, 12, 15),
            time=time(10, 0)
        )

        response = self.client.post(
            '/api/bookings/',
            {
                'tour': self.tour.id,
                'date': '2026-12-15',
                'time': '10:00:00'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    # 5. Разрешение другого времени
    def test_booking_another_time(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            date=date(2026, 12, 15),
            time=time(10, 0)
        )

        response = self.client.post(
            '/api/bookings/',
            {
                'tour': self.tour.id,
                'date': '2026-12-15',
                'time': '14:00:00'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

    # 6. Проверка связи 1:M
    def test_user_multiple_bookings(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            date=date(2026, 12, 15),
            time=time(10, 0)
        )

        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            date=date(2026, 12, 16),
            time=time(10, 0)
        )

        self.assertEqual(self.user.bookings.count(), 2)

    # 7. Запрет отзыва о непосещённом туре
    def test_review_without_visit(self):
        response = self.client.post(
            '/api/reviews/',
            {
                'tour': self.tour.id,
                'comment': 'Отличный тур!',
                'rating': 5
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    # 8. Разрешение отзыва о посещённом туре
    def test_review_after_visit(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            date=date(2026, 12, 15),
            time=time(10, 0),
            attended=True
        )

        response = self.client.post(
            '/api/reviews/',
            {
                'tour': self.tour.id,
                'comment': 'Очень понравилось!',
                'rating': 5
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

    # 9. Несколько отзывов к одному туру
    def test_multiple_reviews(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            date=date(2026, 12, 15),
            time=time(10, 0),
            attended=True
        )

        for comment in ['Отлично!', 'Красивые виды!', 'Советую!']:
            response = self.client.post(
                '/api/reviews/',
                {
                    'tour': self.tour.id,
                    'comment': comment,
                    'rating': 5
                },
                format='json'
            )

            self.assertEqual(response.status_code, 201)

        self.assertEqual(Review.objects.filter(
            user=self.user,
            tour=self.tour
        ).count(), 3)

    # 10. Проверка неправильного рейтинга
    def test_invalid_rating(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            date=date(2026, 12, 15),
            time=time(10, 0),
            attended=True
        )

        response = self.client.post(
            '/api/reviews/',
            {
                'tour': self.tour.id,
                'comment': 'Проверка',
                'rating': 10
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
