from django.contrib.auth.forms import ReadOnlyPasswordHashField
from unfold.admin import forms

from apps.authentication.models import User


class UserCreationForm(forms.ModelForm):
    """
    Форма для создания новых пользователей с обязательным паролем
    """
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'full_name', 'role')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.startswith('+996'):
            raise forms.ValidationError("Номер телефона должен начинаться с '+996'.")
        return phone_number

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Форма для изменения существующих пользователей
    """
    password = ReadOnlyPasswordHashField(
        label="Текущий пароль",
        help_text=("Вы можете изменить пароль, воспользовавшись полем ниже."),
        required=False
    )

    new_password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = User
        fields = ['phone_number', 'full_name', 'role', 'password', 'new_password']

    def clean_password(self):
        return self.initial["password"]  # Возвращаем текущий пароль

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        new_password = self.cleaned_data.get('new_password')

        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
        return user
