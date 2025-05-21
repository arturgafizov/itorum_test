from django.utils import timezone

from source.celery import app


@app.task(name='send_booking_cancellation_confirmation', queue='high_priority')
def send_booking_cancellation_confirmation(
        booking_id: int,
):
    from apps.events.models import Notice, Booking
    booking = Booking.objects.get(id=booking_id)
    message = f'Вы {booking.user}  записаны на событие {booking.event.title}, начало в {booking.event.start_time}. ' \
              f'Номер записи № {booking_id}'
    Notice.objects.create(user_id=booking.user, message=message)
    print(message)


@app.task(name='send_booking_confirmation', queue='high_priority')
def send_booking_confirmation(
        booking_id: int,
):
    from apps.events.models import Notice, Booking
    booking = Booking.objects.get(id=booking_id)
    message = f'Уведомляем Вас  {booking.user}, что ваша запись № {booking.pk} отменена на событие {booking.event.title}, ' \
              f'начало в {booking.event.start_time}.'
    Notice.objects.create(user_id=booking.user, message=message)
    print(message)


@app.task(name='notice.soon_start_event', queue='high_priority')
def send_soon_start_event(
        booking,
):
    from apps.events.models import Notice
    message = f'Уведомляем Вас {booking.user} что событие {booking.event.title} по запись № {booking.pk} начнется , ' \
              f'в {booking.event.start_time}.'
    Notice.objects.create(user_id=booking.user, message=message)
    print(message)


@app.task(name='cron_task_send_notice_before_event', queue='high_priority')
def cron_task_send_notice_before_event():
    from apps.events.models import Event
    after_date = timezone.now().date()
    before_date = timezone.now().date() + timezone.timedelta(days=1)
    today_events = Event.objects.filter(status=Event.PENDING, start_time__gte=after_date,
                                        start_time__lte=before_date).order_by('-start_time')
    print('cron_task_send_notice_before_event')
    for event in today_events:
        if event.start_time - timezone.timedelta(hours=1) >= timezone.now():
            bookings = event.bookings.all()
            for booking in bookings:
                send_soon_start_event.delay(booking)


@app.task(name='cron_task_check_event_status', queue='low_priority')
def cron_task_check_event_status():
    from apps.events.models import Event
    after_date = timezone.now().date()
    before_date = timezone.now().date() + timezone.timedelta(days=1)
    today_events = Event.objects.filter(status=Event.PENDING, start_time__gte=after_date,
                                        start_time__lte=before_date).order_by('-start_time')
    print('cron_task_check_event_status')
    for event in today_events:
        if event.start_time + timezone.timedelta(hours=2) >= timezone.now():
            event.status = Event.COMPLETED
            event.save()
