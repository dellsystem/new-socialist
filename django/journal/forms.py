from django import forms

from journal.models import ArticleDetails


class ArticleDetailsForm(forms.ModelForm):
    class Meta:
        model = ArticleDetails
        fields = ['twitter_text', 'facebook_text', 'screenshot_1', 'screenshot_2']
        widgets = {
            'twitter_text': forms.Textarea(attrs={'rows': 3}),
            'facebook_text': forms.Textarea(attrs={'rows': 3}),
        }
