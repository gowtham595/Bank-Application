from django import forms
from bankapp.models import reg

class regform(forms.ModelForm):
    confirm_pass=forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=reg
        fields=['accno','name','password','amount','address','mobileno']
        widgets={"password":forms.PasswordInput(),"address":forms.Textarea()}

        #verfying password
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_pass = cleaned_data.get('confirm_pass')

        if password != confirm_pass:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
class balform(forms.Form):
    accno=forms.CharField(widget=forms.NumberInput)
    password=forms.CharField(widget=forms.PasswordInput)

class depform(forms.Form):
    accno=forms.CharField(widget=forms.NumberInput,max_length=10)
    password=forms.CharField(widget=forms.PasswordInput)
    deposit=forms.CharField(widget=forms.NumberInput,max_length=10)

class withdrawform(forms.Form):
    accno=forms.CharField(widget=forms.NumberInput,max_length=10)
    password=forms.CharField(widget=forms.PasswordInput)
    withdraw=forms.FloatField()

class transferform(forms.Form):
    accno=forms.CharField(max_length=20,widget=forms.NumberInput)
    name=forms.CharField(max_length=30)
    password=forms.CharField(max_length=10,widget=forms.PasswordInput)
    target_account=forms.CharField(max_length=20,widget=forms.NumberInput)
    amount=forms.FloatField()

class closeform(forms.Form):
    accno=forms.CharField(max_length=20,widget=forms.NumberInput)
    name=forms.CharField(max_length=30)
    password=forms.CharField(max_length=10,widget=forms.PasswordInput)  