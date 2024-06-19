from django.urls import path
from movies.api.v1 import views

urlpatterns = [
    path('movies/<uuid:get_pk>', views.MoviesDetailApi.as_view()),
    path('movies/', views.MoviesListApi.as_view()),
]
