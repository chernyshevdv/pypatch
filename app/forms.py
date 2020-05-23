from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, BooleanField, IntegerField, StringField, HiddenField


class UploadForm(FlaskForm):
    file = FileField('Report file')
    new_deployment = BooleanField("It's a new deployment", default=False)
    new_cycle = BooleanField("It's a new cycle", default=False)
    submit = SubmitField('Submit')


class DeploymentForm(FlaskForm):
    id = IntegerField()
    title = StringField()
    submit = SubmitField()


class CollectionForm(FlaskForm):
    id = HiddenField()
    title = StringField()
    ring = IntegerField()
    cycle_id = HiddenField()
    submit = SubmitField()
