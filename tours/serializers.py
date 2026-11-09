
from rest_framework import serializers
from .models import UserProfile, Category, Tour, Booking, Review


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'attended', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, attrs):
        user = self.context['request'].user
        date = attrs['date']
        time = attrs['time']

        exists = Booking.objects.filter(
            user=user,
            date=date,
            time=time
        ).exists()

        if exists:
            raise serializers.ValidationError(
                'Вы уже забронировали тур на это время.'
            )

        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate(self, attrs):
        request = self.context['request']
        tour = attrs.get(
            'tour',
            self.instance.tour if self.instance else None
        )

        visited = Booking.objects.filter(
            user=request.user,
            tour=tour,
            attended=True
        ).exists()

        if not visited:
            raise serializers.ValidationError(
                'Нельзя оставить отзыв о непосещённом туре.'
            )

        return attrs

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Рейтинг должен быть от 1 до 5.'
            )
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

