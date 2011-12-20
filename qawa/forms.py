from django.forms import Form, RegexField, CharField

class AuthForm(Form):
    username = RegexField(
        label='Phone number', 
        regex=r'^\+?\d{10,12}$',
        help_text = 'Required. Valid phone number in the format: 0821234567 or +27821234567',
        error_message = 'Please enter a valid phone number without spaces. e.g 0821234567 or +27821234567',
        required = True)
    password = CharField(required = True)

class RegisterForm(Form):
    username = RegexField(
        label='Phone number', 
        regex=r'^\+?\d{10,12}$',
        help_text = 'Required. Valid phone number in the format: 0821234567 or +27821234567',
        error_message = 'Please enter a valid phone number without spaces. e.g 0821234567 or +27821234567',
        required = True)