from django import forms

class Dimensions(forms.Form):
    carriage_way = forms.FloatField(label="Carriage way in 'm'", min_value=7.0, max_value=10.0, required=True, widget=forms.NumberInput(attrs={'step': '0.1'}))
    foot_path = forms.FloatField(label="Foot Paths on either side in 'm'", min_value=0, max_value=1.2, required=True, widget=forms.NumberInput(attrs={'step': '0.1'}))
    span = forms.IntegerField(label="Clear Span in 'm'", min_value=5, max_value=10, required=True)
    bearing_width = forms.IntegerField(label="Width of bearing in 'mm'", min_value=0, required=True)
    wear_coat = forms.IntegerField(label="Thickness of wearing coat in 'mm'", min_value=0, required=True)