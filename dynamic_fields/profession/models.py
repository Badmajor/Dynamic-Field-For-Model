from django.core.exceptions import ValidationError
from django.db import models


from .consts import TYPE_FIELD


class BaseModel(models.Model):
    title = models.CharField(max_length=64, verbose_name="Название")

    class Meta:
        abstract = True


class DynamicField(BaseModel):
    type = models.CharField(
        choices=TYPE_FIELD,  # Добавляя новый тип данных, необходимо добавить валидацию в /recruitment/forms.py
        max_length=16,
        verbose_name="Тип поля",
    )
    required = models.BooleanField(default=False, verbose_name="Поле обязательное?")
    choices = models.JSONField(
        blank=True, null=True, help_text="Введите варианты через запятую"
    )

    class Meta:
        verbose_name = "дополнительное поле"
        verbose_name_plural = "Дополнительные поля"

    def __str__(self):
        return self.title

    def clean(self):
        if self.type == "choice" and len(self.choices) < 2:
            raise ValidationError(
                {
                    "choices": "ввести минимум два варианта, "
                    "когда добавляете поле выбора значения"
                }
            )


class Profession(BaseModel):
    description = models.TextField(max_length=512, verbose_name="Описание")
    extra_fields = models.ManyToManyField("DynamicField", through="FieldProfession")

    class Meta:
        verbose_name = "профессия"
        verbose_name_plural = "Профессии"

    def __str__(self):
        return self.title


class FieldProfession(models.Model):
    dynamic_field = models.ForeignKey(DynamicField, on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Дополнительное поле профессии"
        verbose_name_plural = "Дополнительные поля профессии"


class Vacancy(BaseModel):
    profession = models.ForeignKey(
        Profession,
        on_delete=models.CASCADE,
        verbose_name="Профессия",
    )
    company = models.CharField(
        max_length=100, verbose_name="Компания"
    )  # TODO нужна отдельная таблица с компаниями
    posted_date = models.DateTimeField(auto_now_add=True)
    extra_fields = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return self.title
