from django.db.models import Case, When, Value, IntegerField, F, DateTimeField, Q
from django.utils import timezone

from apps.events import models

class EventServices:

    @staticmethod
    def default_sorted():
        return models.Event.objects.select_related('organizer').annotate(
                sort_order=Case(
                    When(
                        Q(status=models.Event.PENDING) & Q(start_time__gt=timezone.now()),
                        then=Value(0)
                    ),
                    When(
                        Q(status=models.Event.COMPLETED) | Q(start_time__lte=timezone.now()),
                        then=Value(1)
                    ),
                    When(
                        status=models.Event.CANCELLED,
                        then=Value(2)
                    ),
                    output_field=IntegerField(),)
                    ).annotate(
                        sort_datetime=Case(
                            When(sort_order=0, then=F('start_time')),
                            default=F('created_at'),
                            output_field=DateTimeField()
                        )
                    ).order_by('sort_order', 'sort_datetime')

    @staticmethod
    def user_events(user_id):
        return models.Event.objects.select_related('organizer').filter(
            organizer_id=user_id, status=models.Event.PENDING).order_by('start_time')