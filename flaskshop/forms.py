from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user, UserMixin
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flaskshop.models import User

# KEITH: DISABLED VALIDATORS
# THOMAS: Enabled validators to show min and max password length to attackers

class Users(UserMixin):
    def __init__(self, username, admin):
        self.username = username
        self.isadmin = admin
    def is_authenticated(self):
        return True
    def get_id(self):
        return self.username
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def is_admin(self):
        return self.isadmin


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()]#, Length(min=2, max=20)]
                           )
    email = StringField('Email',
                        validators=[DataRequired()]#, Email()]
                        )
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=1, max=15)]
                             )
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired()]#, EqualTo('password')]
                                     )
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired()]#, Email()]
                        )
    password = PasswordField('Password',
                             validators=[DataRequired()]
                             )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()]#, Length(min=2, max=20)])
                           )
    email = StringField('Email',
                        validators=[DataRequired(), Email()]
                        )
    # Thomas: shows password in account page
    password = StringField('Password',
                           validators=[DataRequired(), Length(min=1, max=15)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = DecimalField('Price', validators=[NumberRange(min=1, max=9999), DataRequired()], default=0)
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0, max=9999)], default=0)
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField("List Product")


class CheckoutForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    postal = StringField('Postal Code', validators=[DataRequired()])
    cardNumber = StringField('Card Number', validators=[DataRequired()])
    expDate = StringField('Exp Month', validators=[DataRequired()])
    cvv = IntegerField('CVV', validators=[DataRequired()])
    submit = SubmitField("Submit", render_kw={'class': 'btn btn-success btn-block'})


class SearchForm(FlaskForm):
    search = StringField('search')
    submit = SubmitField("Seach", render_kw={'class': 'btn btn-success btn-block'})


class ContactUsForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField("Submit")