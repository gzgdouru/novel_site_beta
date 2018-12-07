from django import forms


class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=20, required=True)