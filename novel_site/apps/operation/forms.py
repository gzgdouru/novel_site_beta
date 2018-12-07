from django import forms


class SuggestForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    suggest = forms.CharField(widget=forms.Textarea, required=True)