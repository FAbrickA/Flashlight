from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, \
    SubmitField, PasswordField, SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, EqualTo, Email, NumberRange, DataRequired
from wtforms import widgets


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    # TODO ограничения на длину логина
    login = StringField("Логин / email", validators=[InputRequired()])
    password = PasswordField("Пароль", validators=[InputRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):  # pip install wtforms[email]
    login = StringField("Логин", validators=[InputRequired(message="Введите логин")])
    email = EmailField("Email",
                       validators=[
                           InputRequired(),
                           Email(check_deliverability=True, message="Некорректный email")
                       ])
    password = PasswordField("Пароль",
                             validators=[
                                 InputRequired(),
                                 EqualTo('password_repeat', message="Пароли должны совпадать")
                             ])
    password_repeat = PasswordField("Повторите пароль", validators=[InputRequired()])
    submit = SubmitField("Зарегистрироваться")


class EditProjectForm(FlaskForm):
    # TODO ограничения на длину заголовка и описания
    #
    # def __init__(self):
    #     __db = db_session.create_session()
    #     __categories_list = __db.query(Category).all()
    #     self.categories = MultiCheckboxField(
    #         "Категории",
    #         validators=[InputRequired()],
    #         choices=[__category.name for __category in __categories_list]
    #     )
    upload_photo = FileField("Загрузить фото",
                             validators=[
                                 DataRequired(),
                                 FileAllowed(['jpg', 'jpeg', 'png', 'bmp'], message="Только картинки!")
                             ])
    budget = IntegerField("Бюджет",
                          validators=[
                              DataRequired(),
                              NumberRange(min=1000, max=10000000,
                                          message="Слишком маленькая \\ большая сумма")
                          ])
    title = StringField("Заголовок", validators=[InputRequired()])
    short_desc = StringField("Краткое описание", validators=[InputRequired()])
    full_desc = TextAreaField("Полное описание", validators=[InputRequired()])
    submit = SubmitField("Создать проект")


class PaymentForm(FlaskForm):
    payment = IntegerField("Оплата",
                           validators=[
                               DataRequired(),
                               NumberRange(min=50, max=10000000,
                                           message="Слишком маленькая \\ большая сумма")
                           ])
    submit = SubmitField("Внести")
