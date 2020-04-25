from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import PasswordField, BooleanField, SubmitField


class NewLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')


class ReturningLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class artistsform:
    @staticmethod
    def form(dropdown_list):
        class F(FlaskForm):
            listener_sel = SelectField('Listener', choices= [(x,x) for x in dropdown_list])
            submit = SubmitField('Submit')
        return F()


class timespanform:
    @staticmethod
    def form(dropdown_list):
        class F(FlaskForm):
            timespan_sel = SelectField('Time Span', choices= [(x,x) for x in dropdown_list])
            submit = SubmitField('Submit')
        return F()
        


