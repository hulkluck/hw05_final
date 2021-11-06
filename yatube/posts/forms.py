from django import forms
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:

        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст'),
            'group': _('Группа'),
            'image': _('Картинка')
        }
        help_texts = {
            'text': _('Здесь пишите много букв своего поста =)'),
            'group': _('Выберите группу из списка'),
            'image': _('Загрузите ваше изображение'),
        }

        def clean_text(self):
            text = self.cleaned_data['text']

            if text == '':
                raise forms.ValidatorError(
                    'В посте обязательно должен быть текст'
                )
            return text


class CommentForm(forms.ModelForm):

    class Meta:

        model = Comment
        fields = ('text',)
        labels = {'text': _('Текст комментария')}
        help_texts = {
            'text': _('Здесь пишите много букв своего комментария =)')}

        def clean_text(self):
            text = self.cleaned_data['text']
            if text == '':
                raise forms.ValidatorError(
                    'В посте обязательно должен быть текст'
                )
            return text
