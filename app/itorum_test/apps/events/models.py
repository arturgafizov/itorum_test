from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.events.task import send_booking_cancellation_confirmation, send_booking_confirmation

User = get_user_model()


class Tag(models.Model):
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    STATUS_CHOICES = {
        PENDING: PENDING,
        CANCELLED: CANCELLED,
        COMPLETED: COMPLETED,
    }
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)
    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание', db_index=True)
    start_time = models.DateTimeField(verbose_name='Время начала')
    location = models.CharField(verbose_name='Локация (город)', max_length=100)
    capacity = models.PositiveIntegerField(verbose_name='Количество мест')
    status = models.CharField(
        verbose_name='Статус',
        max_length=32,
        choices=sorted(STATUS_CHOICES.items()),
        default=PENDING,
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Организатор'
    )
    tags = models.ManyToManyField(Tag, related_name='events', blank=True, verbose_name='Теги')

    def save(self,  *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if timezone.now() >= self.start_time - timezone.timedelta(hours=1):
            raise ValidationError('Удаление события возможно только за час до начала или раньше.')
        super().delete(*args, **kwargs)

    @property
    def positive_capacity(self) -> bool:
        return self.capacity > 0

    def add_capacity(self):
        self.capacity -= 1
        if self.capacity == 0:
            self.status = Event.COMPLETED  # Можно закрыть регистрацию
        self.save()

    def minus_capacity(self):
        self.capacity += 1
        self.save()


    def validate_book_event(self):
        if self.status != Event.PENDING:
            raise ValidationError("Событие не активно.")
        if not self.positive_capacity:
            raise ValidationError("Нет доступных мест.")

    def validate_cancel_event(self):
        if self.status != Event.PENDING:
            raise Exception("Невозможно отменить бронь для завершенного или отмененного события.")

    @staticmethod
    def change_status(event_id: int, organizer_id: int , status: str):
        original = Event.objects.get(pk=event_id)
        if original.organizer_id != organizer_id:
            raise ValidationError('Изменение не организатором запрещено.')
        original.status = status
        original.save()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class Booking(models.Model):
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Пользователь'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Событие'
    )
    booked_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    @transaction.atomic
    def book_event(user_id, event_id):
        event = Event.objects.select_for_update().get(id=event_id)
        event.validate_book_event()
        booking, created = Booking.objects.get_or_create(user_id=user_id, event=event)
        if not created:
            raise ValidationError("Вы уже забронировали это событие.")
        event.add_capacity()
        transaction.on_commit(
            lambda: send_booking_confirmation.delay(
                booking_id=booking.id,
            )
        )
        return event

    @staticmethod
    @transaction.atomic
    def cancel_booking(user_id, event_id):
        try:
            booking = Booking.objects.select_for_update().get(user_id=user_id, event_id=event_id)
        except Booking.DoesNotExist:
            raise ValidationError("Бронирование не найдено.")

        event = booking.event
        event.validate_cancel_event()
        event.minus_capacity()
        booking.delete()
        transaction.on_commit(
            lambda: send_booking_cancellation_confirmation.delay(
                booking_id=booking.id,
            )
        )
        return event

    class Meta:
        unique_together = ('user', 'event')


class Notice(models.Model):
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлено', auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notices')
    message = models.TextField()

    def __str__(self):
        return f'Notice for {self.user}_{self.user.email} - {self.message[:20]}'