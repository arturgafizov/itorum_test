import django_filters
from apps.events.models import Event

class EventTagFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='tags__name', lookup_expr='icontains')
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains')
    start_date = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='icontains')
    positive_capacity = django_filters.BooleanFilter(method='filter_positive_capacity')

    class Meta:
        model = Event
        fields = ['tags', 'status', 'location', 'start_date', 'positive_capacity']

    def filter_positive_capacity(self, queryset, name, value):
        if value is True:
            return queryset.filter(capacity__gt=0)
        elif value is False:
            return queryset.filter(capacity__lte=0)
        return queryset