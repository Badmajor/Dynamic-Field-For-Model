from django import forms

from .models import DynamicField, Vacancy


class VariantsField(forms.Field):
    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(",")]

    def prepare_value(self, value):
        if value:
            return ", ".join(value)
        return value


class DynamicFieldForm(forms.ModelForm):
    choices = VariantsField(required=False, help_text="Введите варианты через запятую")

    class Meta:
        fields = ["title", "type", "required", "choices"]
        model = DynamicField


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = (
            "title",
            "profession",
            "company",
        )

    def clean(self):
        cleaned_data = super().clean()
        profession = self.cleaned_data.get("profession")
        if profession:
            extra_fields = profession.extra_fields.all()
            for field in extra_fields:
                value = cleaned_data.get(field.title, None)
                if value:
                    self.validate_field(field, value)
        return cleaned_data

    def validate_field(self, field, value):
        if field.type == "choice" and value not in field.choices:
            self.add_error(field.title, "Выберите вариант из представленных")
        if field.type == "str" and not isinstance(value, str):
            self.add_error(field.title, "Это поле должно быть строкой")
        elif field.type == "int" and not value.isdigit():
            self.add_error(field.title, "Это поле должно быть числом")

    def save(self, commit=True):
        vacancy = super().save(commit=False)
        extra_fields_titles = [
            field.title for field in vacancy.profession.extra_fields.all()
        ]
        extra_fields = {}
        for field in extra_fields_titles:
            if field in self.data:
                extra_fields[field] = self.data.get(field)
        vacancy.extra_fields = extra_fields
        if commit:
            vacancy.save()
        return vacancy
