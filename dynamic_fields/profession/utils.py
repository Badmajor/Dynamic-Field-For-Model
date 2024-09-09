from django import forms


def get_extra_fields(obj) -> dict:
    fields = {}
    extra_fields = obj.extra_fields.all()
    for field in extra_fields:
        if field.type == "choice":
            choices = [(choice, choice) for choice in field.choices]
            fields[f"{field.title}"] = forms.ChoiceField(
                label=field.title,
                choices=choices,
                required=field.required,
            )
        else:
            fields[f"{field.title}"] = forms.CharField(
                label=field.title,
                required=field.required,
            )
    return fields


def add_extra_fields(form, fields: dict):
    for field_name, field in fields.items():
        form.base_fields[field_name] = field
