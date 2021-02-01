from django import forms
from .models import Metar

class MetarForm(forms.ModelForm):
    siteID = forms.CharField(label='METAR ID',widget=forms.TextInput(attrs={"placeholder":"4-Letter ID"}))
    class Meta:
        model = Metar
        fields = [
            'siteID',
            'Lat',
            'Lon'
        ]
    def clean_siteID(self,*args, **kwargs):
        siteID = self.cleaned_data.get("siteID")
        if len(siteID) != 4:
            raise forms.ValidationError("Site ID must be 4 characters long.")
        return siteID


class RawMetarForm(forms.Form):
    siteID = forms.CharField()
    Lat = forms.DecimalField()
    Lon = forms.DecimalField()