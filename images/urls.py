from django.urls import path
from . import views


urlpatterns = [
    path('create/',views.image_create,name='image_create'),
    path('image/all',views.list_image,name='list_image'),
    path('detail/<int:id>/<slug:slug>/', views.image_detail, name='detail'),
    path('like/', views.image_like, name='like'),
    path('comment/', views.image_comment, name='comment'),
    path('ranking/', views.image_ranking, name='ranking'),
    path('delete/<int:id>/', views.delete_bookmark_image, name='delete_bookmark_image'),
    path('edit/<int:id>/', views.edit_image, name='edit_image'),
    path('image_upload/',views.image_upload,name='image_upload')
]

