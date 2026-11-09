
from django.db import models
from django.contrib.auth.models import User


# 1:1 — Один пользователь имеет один профиль
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


# Категории туров
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Информация о туре
class Tour(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # M:M — Один тур может иметь несколько категорий
    categories = models.ManyToManyField(
        Category,
        related_name='tours'
    )

    def __str__(self):
        return self.title


# 1:M — Один пользователь может иметь много бронирований
class Booking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    date = models.DateField()
    time = models.TimeField()

    attended = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date', 'time'],
                name='unique_user_booking_datetime'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.tour.title}'


# Один пользователь может оставить несколько отзывов
class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.tour.title}'

