from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from tinymce.widgets import TinyMCE

from content.models import ContentCategory, Rewards, Comments


class ContentCategoryForm(forms.ModelForm):
    """
        form to add
    """

    class Meta:
        model = ContentCategory
        fields = ['category']


class RewardForm(forms.ModelForm):
    class Meta:
        model = Rewards
        fields = ['token', 'target', 'target_type', 'reward_badge']

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': 'Reward for this target already exists'
            }
        }


class AddContentForm(forms.Form):
    title = forms.CharField(max_length=100)
    category = forms.CharField(max_length=100)
    data = forms.CharField(widget=TinyMCE(attrs={'cols': 10, 'rows': 6}))

    def clean_data(self):
        data = self.cleaned_data['data']
        if len(data) < 10:
            raise forms.ValidationError("Textarea must be at least 10 characters long.")
        return data


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']
