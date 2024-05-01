from django.urls import path
from .views import upload, result


urlpatterns = [
    path('', upload, name='upload'),
    path('result/', result, name='result'),
]
