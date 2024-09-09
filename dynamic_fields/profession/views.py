from django.views.generic import ListView

from . import models


class VacancyListView(ListView):
    model=models.Vacancy


class ProfessionListView(ListView):
    model = models.Profession