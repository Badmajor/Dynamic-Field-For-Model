from django.contrib import admin
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.urls import path


from .forms import DynamicFieldForm, VacancyForm
from .models import DynamicField, Profession, Vacancy
from .utils import add_extra_fields, get_extra_fields


class DynamicFieldInline(admin.TabularInline):
    model = Profession.extra_fields.through
    readonly_fields = ["dynamic_field_required", "dynamic_field_type"]
    extra = 1

    def get_fields(self, request, obj=None):
        fields = ["dynamic_field", "dynamic_field_required", "dynamic_field_type"]
        if obj:
            if any(field.type == "choice" for field in obj.extra_fields.all()):
                fields += ["dynamic_field_choices"]
                self.readonly_fields += ["dynamic_field_choices"]
        return fields

    def dynamic_field_required(self, instance):
        return "✅" if instance.dynamic_field.required else ""

    def dynamic_field_type(self, instance):
        return instance.dynamic_field.type

    def dynamic_field_choices(self, instance):
        return ", ".join(map(str, instance.dynamic_field.choices))

    dynamic_field_required.short_description = "Обязательное?"
    dynamic_field_type.short_description = "Тип"
    dynamic_field_type.short_description = "Варианты"


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    inlines = (DynamicFieldInline,)


@admin.register(DynamicField)
class DynamicFieldModelAdmin(admin.ModelAdmin):
    form = DynamicFieldForm
    fieldsets = (
        (None, {"fields": ("title", "type", "required")}),
        ("Choices", {"fields": ("choices",), "classes": ("collapse",)}),
    )


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "select-profession/",
                self.admin_site.admin_view(self.select_profession),
                name="select-profession",
            ),
        ]
        return custom_urls + urls

    def select_profession(self, request):
        if request.method == "POST":
            selected_profession = request.POST.get("profession")
            url = (
                reverse("admin:profession_vacancy_add")
                + f"?profession_id={selected_profession}"
            )
            return redirect(url)
        context = {"professions": Profession.objects.all()}
        return render(request, "admin/select-profession.html", context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id or request.GET.get("profession_id"):
            return super().changeform_view(request, object_id, form_url, extra_context)
        return redirect("admin:select-profession")

    def get_form(self, request, obj=None, **kwargs):
        form = VacancyForm
        profession_id = (
            request.GET.get("profession_id") if not obj else obj.profession.id
        )
        profession = get_object_or_404(Profession, pk=profession_id)
        form.base_fields["profession"].initial = profession_id

        extra_fields = get_extra_fields(profession)
        add_extra_fields(form, fields=extra_fields)

        if obj:
            for title, value in obj.extra_fields.items():
                form.base_fields[title].initial = value
        return form
