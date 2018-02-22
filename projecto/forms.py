from wtforms import (StringField, TextAreaField, FieldList, FormField,
                     validators, Form, Field, ValidationError)
from wtforms.widgets import TextInput
from flask_wtf import FlaskForm
from flask_security.forms import RegisterForm

from projecto.db_operations import check_if_author_exists


class TagField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_data(self, value):
        if value:
            self.data = [str(val.id) for val in value]
        else:
            self.data = []

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []

 # a tweaked StringField that strips values to exclude
 # incorrect addition, editing and sorting behaviour
class CleanStringField(StringField):
    def process_formdata(self, valuelist):
        super(CleanStringField, self).process_formdata(valuelist)
        self.data = self.data.strip()


class AuthorsSearchForm(Form):
    name = CleanStringField('Name', [validators.Length(max=50)])
    surname = CleanStringField('Surname', [validators.Length(max=50),
                                      validators.Optional()])
    book_title = CleanStringField('Book title', [validators.Optional()])


class SimpleBookForm(Form):
    title = CleanStringField('Title', [validators.Length(max=200)])
    overview = TextAreaField('Description', [validators.Optional(),
                                             validators.Length(max=2000)])
    content = TextAreaField('Content')


class AddAuthorForm(FlaskForm):
    first_name = CleanStringField('First name', [validators.Length(max=50),
                                            validators.InputRequired()])
    last_name = CleanStringField('Last name', [validators.Length(max=50),
                                          validators.Optional()])
    description = TextAreaField('Description', [validators.Optional(),
                                                validators.Length(max=2000)])
    books = FieldList(FormField(SimpleBookForm), min_entries=1)


class EditAuthorForm(FlaskForm):
    name = CleanStringField('First name', [validators.Length(max=50),
                                      validators.InputRequired()])
    surname = CleanStringField('Last name', [validators.Length(max=50),
                                        validators.Optional()])
    description = TextAreaField('Description', [validators.Optional(),
                                                validators.Length(max=2000)])
    books = TagField('Books')


class AddBookForm(FlaskForm):
    title = CleanStringField('Title', [validators.Length(max=200),
                                  validators.InputRequired()])
    description = TextAreaField('Description', [validators.Optional(),
                                                validators.Length(max=2000)])
    text = TextAreaField('Content', [validators.InputRequired()])
    authors = TagField('Authors', [validators.InputRequired()])

    def validate_authors(form, field):
        if not check_if_author_exists(field.data):
            raise ValidationError('Incorrect author id')


# security forms
class UpgradedRegisterForm(RegisterForm):
    username = CleanStringField('Username', [validators.Length(max=100),
                                        validators.InputRequired()])
