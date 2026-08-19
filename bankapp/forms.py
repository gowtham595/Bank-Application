from django import forms
from django.core.validators import MinValueValidator
from bankapp.models import reg


class regform(forms.ModelForm):
    confirm_pass = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = reg
        fields = ['accno', 'name', 'password', 'amount', 'address', 'mobileno']
        widgets = {
            "password": forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            "accno": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            "amount": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Initial Deposit'}),
            "address": forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            "mobileno": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
        }

    def clean_accno(self):
        accno = self.cleaned_data.get('accno')
        if reg.objects.filter(accno=accno).exists():
            raise forms.ValidationError("Account number already exists.")
        return accno

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError("Initial deposit cannot be negative.")
        return amount

    def clean_mobileno(self):
        mobile = self.cleaned_data.get('mobileno')
        if not mobile.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(mobile) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_pass = cleaned_data.get('confirm_pass')

        if password and confirm_pass and password != confirm_pass:
            raise forms.ValidationError("Passwords do not match.")

        if password and len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")

        return cleaned_data


class balform(forms.Form):
    accno = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
        label="Account Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )


class depform(forms.Form):
    accno = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
        label="Account Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )
    deposit = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount to Deposit'}),
        label="Deposit Amount"
    )


class withdrawform(forms.Form):
    accno = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
        label="Account Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )
    withdraw = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount to Withdraw'}),
        label="Withdrawal Amount"
    )


class transferform(forms.Form):
    accno = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Your Account Number'}),
        label="From Account"
    )
    name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
        label="Your Name"
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )
    target_account = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Recipient Account Number'}),
        label="To Account"
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount to Transfer'}),
        label="Transfer Amount"
    )

    def clean(self):
        cleaned_data = super().clean()
        accno = cleaned_data.get('accno')
        target = cleaned_data.get('target_account')
        if accno and target and str(accno) == str(target):
            raise forms.ValidationError("Cannot transfer to the same account.")
        return cleaned_data


class closeform(forms.Form):
    accno = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
        label="Account Number"
    )
    name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
        label="Account Holder Name"
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )