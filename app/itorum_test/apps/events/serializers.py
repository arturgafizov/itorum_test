from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import serializers

from apps.events import models
from source.utils import CurrentUserIdDefault

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['id', 'name']


class EventCreateSerializers(serializers.ModelSerializer):
    organizer = serializers.IntegerField(default=CurrentUserIdDefault())

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        except IntegrityError:
            raise serializers.ValidationError('event_exists')

    class Meta:
        model = models.Event
        fields = ('id', 'title', 'description', 'start_time', 'location', 'capacity', 'status', 'organizer')


class EventReadSerializers(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = models.Event
        fields = ('id', 'title', 'description', 'start_time', 'location', 'capacity', 'status', 'organizer', 'tags')
        depth = 1


class UpdateStatusEventSerializers(serializers.Serializer):
    organizer_id = serializers.IntegerField(default=CurrentUserIdDefault())
    event_id = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=models.Event.STATUS_CHOICES)

    def save(self):
        event = models.Event.change_status(**self.validated_data)
        return event


class BookingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(default=CurrentUserIdDefault())
    event_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = models.Booking
        fields = ['id', 'event_id', 'user_id']