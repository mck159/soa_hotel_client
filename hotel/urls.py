from django.conf.urls import url

from hotel import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login/$', views.login, name='login'),
    url(r'logout/$', views.logout, name='logout'),
    url(r'register/$', views.register, name='register'),
    url(r'hotels/$', views.hotels, name='hotelList'),
    url(r'hotel/(?P<hotel_id>[0-9]+)/rooms$', views.rooms, name='roomList'),
    url(r'hotel/(?P<hotel_id>[0-9]+)/rooms/(?P<room_id>[0-9]+)/availabilty$', views.roomAvailability, name='roomAvailabilty'),
    url(r'hotel/reservations$', views.reservations, name='reservationList'),
    url(r'hotel/reservations/(?P<reservation_id>[0-9]+)/complaint$', views.complaint, name='complaint'),
    url(r'invoices/$', views.invoices, name='invoiceList'),
    url(r'invoice/(?P<invoice_id>[0-9]+)$', views.invoice, name='invoice'),
    url(r'payments/$', views.payments, name='paymentList'),
    url(r'payments/(?P<payment_id>[0-9]+)/pay$', views.paymentPay, name='paymentPay')
]

