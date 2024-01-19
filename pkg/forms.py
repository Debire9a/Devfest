from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,EmailField,BooleanField,DateField,RadioField
from wtforms.validators import DataRequired,Length,Email,EqualTo

from flask_wtf.file import FileField,FileAllowed,FileRequired

class Breakoutform(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    level = StringField('Level',validators=[DataRequired()])
    image = FileField(validators=[FileRequired()])
    status = BooleanField('Status',validators=[DataRequired()])
    submit = SubmitField('Add Topic!')