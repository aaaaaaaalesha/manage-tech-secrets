import uuid

from django.contrib import admin
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import path, reverse
from django.utils.html import format_html

from apps.users.models import TechSecret, User
from apps.users.services.secret import generate_secret_string, make_hash

_SUCCESS_MSG_TEMPLATE: str = (
    "<strong>Секрет успешно сгенерирован:</strong> <tt>{}</tt> <br>"
    "<strong>Обязательно скопируйте его значение: увидеть его в открытом виде больше не выйдет: "
    "<u>в БД сохранился только его хэш</u>!</strong>"
)


class TechSecretAdmin(admin.ModelAdmin):
    # Добавляет кнопку генерации секрета для суперпользователя.
    change_form_template = "admin/tech_secret/change_form.html"
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__first_name", "user__email")

    def get_readonly_fields(self, request, obj=None):
        custom_ro_fields = ("secret_hash",)
        return super().get_readonly_fields(request, obj=obj) + custom_ro_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # Фильтруем пользователей по типу TECHNICAL.
            kwargs["queryset"] = User.objects.filter(type=User.Type.TECHNICAL)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.type == User.Type.STAFF

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.type == User.Type.STAFF

    def get_urls(self) -> list[path]:
        return [
            path(
                "generate_secret/<int:object_id>/",
                self.admin_site.admin_view(self.generate_secret_view),
                name="generate_secret"
            ),
        ] + super().get_urls()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['generate_secret_url'] = reverse('admin:generate_secret', args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        """Переопределённый метод создания экземпляров TechSecret для автоматической генерации секрета."""
        if request.method != "POST":
            return super().add_view(request, form_url, extra_context=extra_context)

        # POST: при отправке формы создания, генерируем секрет и подставляем его в поле.
        plain_secret_value: str = generate_secret_string()
        secret_hash: str = make_hash(plain_secret_value)
        form = self.get_form(request, None)(request.POST)
        if not form.is_valid():
            return super().add_view(request, form_url, extra_context=extra_context)

        # Создаем объект, но не сохраняем его в БД.
        technical_secret: TechSecret = form.save(commit=False)
        # Патчим значение хэша и теперь сохраняем.
        technical_secret.secret_hash = secret_hash
        technical_secret.creator = request.user
        technical_secret.editor = request.user
        technical_secret.save()
        success_msg = format_html(_SUCCESS_MSG_TEMPLATE, plain_secret_value)
        self.message_user(request, success_msg, level="success")
        # Перенаправляем на страницу изменения объекта.
        view_name = f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change'
        return HttpResponseRedirect(reverse(view_name, args=[technical_secret.id]))

    def generate_secret_view(self, request: HttpRequest, object_id: uuid.UUID) -> HttpResponseRedirect:
        """
        Генерирует новый секрет для технической учётной записи.
        :param request: Экземпляр запроса.
        :param object_id: Идентификатор `TechSecret` в БД.
        :return:
        """
        resp = HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
        if not request.user.is_authenticated or request.user.type != User.Type.STAFF:
            err_msg = ("Для генерации секретов технических УЗ, "
                       f"нужно иметь тип пользователя {User.Type.STAFF.label}")
            self.message_user(request, err_msg, level="error")
            return resp

        plain_secret_value: str = generate_secret_string()
        secret_hash: str = make_hash(plain_secret_value)
        technical_secret: TechSecret = self.get_object(request, object_id)
        if not technical_secret:
            self.message_user(request, "Техническая УЗ не найдена", level="error")
            return resp

        technical_secret.secret_hash = secret_hash
        technical_secret.editor = request.user
        technical_secret.save()
        success_msg = format_html(_SUCCESS_MSG_TEMPLATE, plain_secret_value)
        self.message_user(request, success_msg, level="success")
        return resp
