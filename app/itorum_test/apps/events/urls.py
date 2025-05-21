from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'apps.events'

router = DefaultRouter()
router.register(r'', views.EventViewSet)
urlpatterns = [
    path('user_events', views.UserEventsView.as_view(), name='user_events'),
    path('update_status', views.UpdateStatusView.as_view(), name='update_status'),
    path('description_search', views.DescriptionSearchView.as_view(), name='description_search'),
    path('book_event', views.BookEventView.as_view(), name='book_event'),
    path('cancel_book_event', views.CancelBookEventView.as_view(), name='cancel_book_event'),
]

urlpatterns += router.urls
