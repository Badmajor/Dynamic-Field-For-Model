from django.urls import path

from . import views

urlpatterns = [
    path('vacancies/', views.VacancyListView.as_view(),),
    path('professions/', views.ProfessionListView.as_view(),)
]
