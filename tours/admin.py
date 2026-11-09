from django.contrib import admin
from .models import UserProfile, Category, Tour, Booking, Review

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Tour)
admin.site.register(Booking)
admin.site.register(Review)
