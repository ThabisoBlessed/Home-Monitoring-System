from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class SignIn(FlaskForm):
    email = StringField("Enter Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Enter Password", validators=[DataRequired(),
                                      Length(min=5, max=15)])
    reminder = BooleanField("Remember me")
    submit = SubmitField("Login")


class SignUp(FlaskForm):
    accid = StringField("Account Id",
                        validators=[DataRequired(),
                                    Length(min=4, max=11)])
    fname = StringField("First name",
                        validators=[DataRequired(),
                                    Length(min=2, max=25)])
    lname = StringField("Last Name",
                        validators=[DataRequired(),
                                    Length(min=2, max=25)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(),
                                Length(min=4, max=15)])
    password2 = PasswordField("Confirm Password",
                              validators=[
                                  DataRequired(),
                                  Length(min=4, max=15),
                                  EqualTo("password",
                                          message="Passwords do not match!!!")
                              ])
    reminder = BooleanField("Remember me")
    submit = SubmitField("Register Now")
