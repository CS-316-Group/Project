from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import PasswordField, BooleanField, SubmitField




# found this class that asks users to login. might be a good starting point for
#users login through spotify.
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class artistsform:
    @staticmethod
    def form(dropdown_list):
        class F(FlaskForm):
            artist_sel = SelectField('Artist', choices= [(x,x) for x in dropdown_list])
            submit = SubmitField('Submit')
        return F()


