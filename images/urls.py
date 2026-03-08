from django.urls import path
from . import views


urlpatterns = [
    path('create/',views.image_create,name='image_create'),
    path('image/all',views.list_image,name='list_image'),
    path('detail/<int:id>/<slug:slug>/', views.image_detail, name='detail'),
]
