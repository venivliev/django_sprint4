from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Post, Comment, Category, Location

User = get_user_model()


class _CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title or getattr(obj, "slug", f"Категория #{obj.pk}")


class _LocationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name or f"Локация #{obj.pk}"


class PostForm(forms.ModelForm):
    # Явно задаём поля выбора с кастомными подписями
    category = _CategoryChoiceField(
        queryset=Category.objects.all(),  # отфильтрованные выставим в __init__
        required=True,
        label="Категория",
    )
    location = _LocationChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label="Местоположение",
    )

    pub_date = forms.DateTimeField(
        label="Дата публикации",
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"],
    )

    image = forms.ImageField(label="Изображение", required=False)

    class Meta:
        model = Post
        fields = ("title", "text", "image", "category", "location", "pub_date", "is_published")
        labels = {
            "title": "Заголовок",
            "text": "Текст",
            "is_published": "Опубликовать",
        }
        widgets = {
            "text": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # показываем только опубликованные категории/локации
        self.fields["category"].queryset = Category.objects.filter(is_published=True).order_by("title")
        self.fields["location"].queryset = Location.objects.filter(is_published=True).order_by("name")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {"text": "Комментарий"}
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False, label="E-mail")
    first_name = forms.CharField(required=False, label="Имя")
    last_name = forms.CharField(required=False, label="Фамилия")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Логин",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "username": "Логин",
            "email": "E-mail",
        }
