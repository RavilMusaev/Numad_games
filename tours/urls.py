
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewSet,
    CategoryViewSet,
    TourViewSet,
    BookingViewSet,
    ReviewViewSet
)

router = DefaultRouter()

router.register('profiles', UserProfileViewSet)
router.register('categories', CategoryViewSet)
router.register('tours', TourViewSet)
router.register('bookings', BookingViewSet, basename='booking')
router.register('reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
