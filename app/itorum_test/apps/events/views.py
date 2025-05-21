from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status, mixins

from apps.events import swagger_schemas as schemas, serializers, models, filters
from apps.events.services import EventServices


@method_decorator(name='list', decorator=swagger_auto_schema(**schemas.events_list, ))
class EventViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, ReadOnlyModelViewSet):
    queryset = models.Event.objects.all()
    http_method_names = ('get', 'post', 'delete')
    serializer_class = serializers.EventReadSerializers
    filter_backends = [DjangoFilterBackend]
    filter_class = filters.EventTagFilter

    def get_queryset(self):
        queryset = super().get_queryset().filter(organizer_id=self.request.user.id)
        if self.action == 'list':
            queryset = EventServices.default_sorted()
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.EventCreateSerializers
        else:
            return super().get_serializer_class()

    @method_decorator(name='destroy', decorator=swagger_auto_schema(**schemas.events_destroy, ))
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserEventsView(ListAPIView):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventReadSerializers
    permission_classes = (IsAuthenticated, )

    @method_decorator(name='list', decorator=swagger_auto_schema(**schemas.my_events_list, ))
    def get(self, request, *args, **kwargs):
        events = EventServices.user_events(request.user.id)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateStatusView(CreateAPIView):
    serializer_class = serializers.UpdateStatusEventSerializers
    permission_classes = (IsAuthenticated, )

    @method_decorator(name='post', decorator=swagger_auto_schema(**schemas.update_event_status, ))
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DescriptionSearchView(RetrieveAPIView):
    serializer_class = serializers.EventReadSerializers
    permission_classes = (AllowAny, )

    @method_decorator(name='get', decorator=swagger_auto_schema(**schemas.description_search, ))
    def get(self, request):
        from apps.events.utils import search_events
        query = request.query_params.get('q', None)
        if not query:
            return Response({"error": "Параметр 'q' обязателен"}, status=status.HTTP_400_BAD_REQUEST)
        results = search_events(query)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookEventView(CreateAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = (IsAuthenticated,)

    @method_decorator(name='post', decorator=swagger_auto_schema(**schemas.book_event, ))
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            try:
                models.Booking.book_event(**serializer.validated_data)
                return Response({'status': 'success', 'message': 'Место успешно забронировано.'},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelBookEventView(CreateAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = (IsAuthenticated,)

    @method_decorator(name='post', decorator=swagger_auto_schema(**schemas.cancel_book_event, ))
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                models.Booking.cancel_booking(**serializer.validated_data)
                return Response({'status': 'success', 'message': 'Бронь успешно отменена.'},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)