# helpful libs
import random
import datetime as dt
import math
from pprint import pprint
import io
from PIL import Image
import os

# flask
import flask
from flask import Flask, request, render_template, redirect, url_for

# flask_login
from flask_login import LoginManager, login_user, logout_user, login_required, \
    current_user

# werkzeug
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy
from data import db_session
from data.users import User
from data.projects import Project
from data.categories import Category

# forms
from forms import LoginForm, PaymentForm, EditProjectForm, RegistrationForm

# TODO flask session last page
# TODO 404, 403 handler
# TODO visual bag fix
# TODO image on edit page
# TODO user image
# TODO category and author on project page
# TODO payment system
# TODO advanced design
# TODO new project categories
# TODO footer pages
# TODO sponsors
# TODO registration email submit
# TODO login captcha
# TODO messages system
# TODO moderate tools
# TODO project editing html
# TODO alembic
# TODO different payments
# TODO project author offers
# TODO multi-image project
# TODO project FAQ + comments + news
# TODO lazy load projects on categories pages
# TODO text length limits checking

STATIC_PATH = "static"
DB_PATH = "db/main.db"

app = Flask("Flashlight")
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'test_secret_key_145'
app.config['UPLOAD_FOLDER'] = f"{STATIC_PATH}/img/uploads"


def check_int(number):
    """
    :arg number - int or float
    """
    if int(number) == number:
        return int(number)
    return number


def main():
    db_session.global_init(DB_PATH)
    db_start_preparation()
    app.run()


def db_start_preparation():
    category_names = [
        "Наука",
        "Технологии",
        "Дизайн",
        "Игры",
        "Музыка",
        "Издательство",
        "ПО и приложения",
    ]
    db = db_session.create_session()
    if not db.query(Category).first():
        for category_name in category_names:
            category = Category(name=category_name)
            db.add(category)
        db.commit()


def project_serializer(project: Project, full_info=False, desc_to_print=True):
    db = db_session.create_session()
    categories = []
    for category_id in sorted(map(int, project.categories.split())):
        categories.append(db.query(Category).get(category_id).name)
    founded_percent = round(project.founded / project.budget * 100, 2)
    seconds_left = project.duration - (dt.datetime.utcnow() - project.start_time).total_seconds()
    days_left = math.ceil(seconds_left / 86400)
    result = {
        'id': project.id,
        'name': project.name,
        'short_desc': project.short_desc,
        'image_path': f"img/projects/{project.image_path}",
        'featured': bool(project.featured),
        'days_left': days_left,
        'is_finished': days_left <= 0,
        'founded_percent': check_int(founded_percent),
        'max_100_founded_percent': min(100, check_int(founded_percent)),
        'is_founded': founded_percent >= 100,
        'budget': check_int(project.budget),
        'founded': check_int(project.founded),
        'start_time': project.start_time,
        'categories': categories,
        'categories_str': ", ".join(categories),
        'author_name': project.author.login,
        'author_id': project.author.id,
    }
    if full_info:
        if desc_to_print:
            result['full_desc'] = project.full_desc.split("\n")
        else:
            result['full_desc'] = project.full_desc
    return result


def get_welcome_project():
    db = db_session.create_session()
    featured_projects = db.query(Project).filter(Project.featured == 1).all()
    if featured_projects:
        project = random.choice(featured_projects)
    else:
        project = random.choice(db.query(Project).all())
    project.author  # ленивая подгрузка автора, это важно
    return project


def get_projects_by_category(category_id):
    # TODO limits + offsets
    db = db_session.create_session()
    for project in db.query(Project).all():
        categories = set(map(int, project.categories.split()))
        if category_id in categories:
            project.author  # ленивая подгрузка автора, это важно
            yield project_serializer(project)


def get_projects_all(limit=None):
    db = db_session.create_session()
    if limit is None:
        projects = db.query(Project).all()
    else:
        projects = db.query(Project).limit(limit).all()
    for project in projects:
        project.author  # ленивая подгрузка автора, это важно
        yield project_serializer(project)


def get_projects_recommended(limit=None):
    # TODO система рекоммендаций
    return get_projects_all(limit)


def get_projects_finish_line():
    # TODO limits + offsets
    db = db_session.create_session()
    for project in db.query(Project).all():
        founded_value = project.founded / project.budget
        if 0.8 <= founded_value < 1:
            project.author  # ленивая подгрузка автора, это важно
            yield project_serializer(project)


def get_projects_newly_created():
    # TODO limits + offsets
    db = db_session.create_session()
    now = dt.datetime.utcnow()
    for project in db.query(Project).all():
        if now - project.start_time < dt.timedelta(days=5):
            project.author  # ленивая подгрузка автора, это важно
            yield project_serializer(project)


def get_projects_by_author(user_id):
    # TODO limits + offsets
    db = db_session.create_session()
    for project in db.query(Project).filter(Project.author_id == user_id).all():
        project.author  # ленивая подгрузка автора, это важно
        yield project_serializer(project)


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    return db.query(User).get(user_id)


@app.route("/", methods=["GET"])
def index_page():
    welcome_project = get_welcome_project()
    recommended_projects = get_projects_recommended(3)
    project_blocks = [  # Блоки слайдеров
        {
            'title': "Новые проекты",
            'link': "/category/newly_created",
            'projects': get_projects_newly_created(),
            'id': 'new-projects-slider',
        },
        {
            'title': "Финишная прямая",
            'link': "/category/finish_line",
            'projects': get_projects_finish_line(),
            'id': 'finish-line-projects-slider',
        }
    ]
    return render_template(
        'index.html',
        static_path=STATIC_PATH,
        log_in_link="/login",
        registration_link="/registration",
        welcome_project=project_serializer(welcome_project),
        recommended_projects=recommended_projects,
        blocks=project_blocks,  # Блоки слайдеров
        title="Flashlight"
    )


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        user = None
        if "@" in form.login.data:  # Проверка email
            user = db.query(User).filter(User.email == form.login.data.lower()).first()
        if user is None:  # Проверка login
            user = db.query(User).filter(User.login == form.login.data).first()

        if user is None:
            return render_template(
                'login.html',
                title="Авторизация",
                error="Неправильный логин / email / пароль",
                form=form,
                static_path=STATIC_PATH,
            )

        if not check_password_hash(user.password_hash, form.password.data):
            return render_template(
                'login.html',
                title="Авторизация",
                error="Неправильный логин / email / пароль",
                form=form,
                static_path=STATIC_PATH,
            )

        login_user(user, remember=form.remember_me.data)
        return redirect("/")

    return render_template(
        'login.html',
        title="Авторизация",
        form=form,
        static_path=STATIC_PATH,
    )


@app.route("/registration", methods=["GET", "POST"])
def registration_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_repeat.data:
            form.password.data = ""
            form.password_repeat.data = ""
            return render_template(
                "registration.html",
                title="Регистрация",
                error="Пароли должны совпадать",
                form=form,
                static_path=STATIC_PATH,
            )
        db = db_session.create_session()
        if db.query(User).filter(User.login == form.login.data).first() is not None:
            return render_template(
                "registration.html",
                title="Регистрация",
                error="Такой логин уже зарегистрирован",
                form=form,
                static_path=STATIC_PATH,
            )
        elif db.query(User).filter(User.email == form.email.data).first() is not None:
            return render_template(
                "registration.html",
                title="Регистрация",
                error="Такой email уже зарегистрирован",
                form=form,
                static_path=STATIC_PATH,
            )
        user = User()
        user.login = form.login.data
        user.email = form.email.data
        user.password_hash = generate_password_hash(form.password.data)
        db.add(user)
        db.commit()
        return redirect("/")

    return render_template(
        "registration.html",
        title="Регистрация",
        form=form,
        static_path=STATIC_PATH,
    )


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect("/")


@app.route("/create_project", methods=["GET", "POST"])
@login_required
def create_project_page():
    form = EditProjectForm()
    db = db_session.create_session()
    categories = db.query(Category).all()
    if form.validate_on_submit():
        categories_chosen = []
        for category in categories:
            name = f"category-{category.id}"
            if name in request.form and request.form[name]:
                categories_chosen.append(category)
        if not categories_chosen:
            return render_template(
                'edit-project.html',
                title="Новый проект",
                static_path=STATIC_PATH,
                form=form,
                categories=categories,
                error="Не выбрано ни одной категории",
                submit_button_text="Создать проект",
            )
        try:
            file = form.upload_photo.data
            image = Image.open(file).resize((800, 530))
            if not image.mode == 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            print(e)
            return render_template(
                'edit-project.html',
                title="Новый проект",
                static_path=STATIC_PATH,
                form=form,
                categories=categories,
                error="Некорректное изображение",
                submit_button_text="Создать проект",
            )

        project = Project()
        project.name = form.title.data
        project.short_desc = form.short_desc.data
        project.full_desc = form.full_desc.data
        project.budget = form.budget.data
        project.categories = " ".join(str(category.id) for category in categories_chosen)
        project.author_id = current_user.id
        db.add(project)
        db.commit()
        project.image_path = f"{project.id}/{project.id}_1.jpg"
        folder_to_save = "./" + url_for(STATIC_PATH, filename=f"img/projects/{project.id}")
        if not os.path.exists(folder_to_save):
            os.makedirs(folder_to_save)
        image.save(
            "./" + url_for(STATIC_PATH, filename=f"img/projects/{project.image_path}"),
            quality=95,
        )
        db.commit()

        return redirect(f"/success_created/{project.id}")

    return render_template(
        'edit-project.html',
        title="Новый проект",
        static_path=STATIC_PATH,
        form=form,
        categories=categories,
        submit_button_text="Создать проект",
    )


@app.route("/create_project", methods=["GET", "POST"])
@login_manager.unauthorized_handler
def create_project_page_unauthorized():
    return redirect("/login")


@app.route("/success_created/<int:project_id>")
def success_created_page(project_id):
    return render_template(
        'payment-thanks-window.html',
        title="Проект успешно создан!",
        button_back_text="К проекту",
        project_id=project_id,
        static_path=STATIC_PATH,
    )


@app.route("/payment_thanks/<int:project_id>")
def payment_thanks_page(project_id):
    return render_template(
        'payment-thanks-window.html',
        title="Спасибо за поддержку!",
        button_back_text="Назад к проекту",
        project_id=project_id,
        static_path=STATIC_PATH,
    )


@app.route("/project/<int:project_id>")
def project_page(project_id):
    db = db_session.create_session()
    project = db.query(Project).get(project_id)
    if project is None:
        flask.abort(404)
        return

    return render_template(
        'project.html',
        static_path=STATIC_PATH,
        project=project_serializer(project, full_info=True),
    )


@app.route("/project/support/<int:project_id>", methods=["GET", "POST"])
def project_support_page(project_id):
    db = db_session.create_session()
    project = db.query(Project).get(project_id)
    if project is None:
        flask.abort(404)
        return

    form = PaymentForm()
    if form.validate_on_submit():
        project.founded += form.payment.data
        db.commit()
        print(123)
        return redirect(f"/payment_thanks/{project_id}")

    return render_template(
        'payment.html',
        static_path=STATIC_PATH,
        project=project,
        form=form,
    )


@app.route("/project/edit/<int:project_id>", methods=["GET", "POST"])
@login_required
def project_edit_page(project_id):
    db = db_session.create_session()
    project = db.query(Project).get(project_id)
    if project is None:
        flask.abort(404)
        return

    if project.author_id != current_user.id:
        flask.abort(403)
        return

    form = EditProjectForm()
    project_categories = set(map(int, project.categories.split()))
    categories = db.query(Category).all()
    if form.validate_on_submit():
        categories_chosen = []
        for category in categories:
            name = f"category-{category.id}"
            if name in request.form and request.form[name]:
                categories_chosen.append(category)
        if not categories_chosen:
            return render_template(
                'edit-project.html',
                title="Редактирование проекта",
                static_path=STATIC_PATH,
                form=form,
                categories=categories,
                error="Не выбрано ни одной категории",
                project_categories=project_categories,
                submit_button_text="Сохранить",
            )
        try:
            file = form.upload_photo.data
            image = Image.open(file).resize((800, 530))
            if not image.mode == 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            print(e)
            return render_template(
                'edit-project.html',
                title="Редактирование проекта",
                static_path=STATIC_PATH,
                form=form,
                categories=categories,
                error="Некорректное изображение",
                submit_button_text="Сохранить",
            )

        project.name = form.title.data
        project.short_desc = form.short_desc.data
        project.full_desc = form.full_desc.data
        project.budget = form.budget.data
        project.categories = " ".join(str(category.id) for category in categories_chosen)
        project.image_path = f"{project.id}/{project.id}_1.jpg"
        path = "." + url_for(STATIC_PATH, filename=f"img/projects/{project.image_path}")
        os.remove(path)
        image.save(
            path, quality=95,
        )
        db.commit()

        return redirect(f"/project/{project.id}")
    try:
        with open("." + url_for(STATIC_PATH,
                                filename=f"img/projects/{project.image_path}"),
                  'rb') as file:
            form.upload_photo.data = io.BytesIO(file.read())
    except Exception as e:
        print(e)
    form.title.data = project.name
    form.short_desc.data = project.short_desc
    form.full_desc.data = project.full_desc
    form.budget.data = check_int(project.budget)

    return render_template(
        'edit-project.html',
        title="Редактирование проекта",
        static_path=STATIC_PATH,
        form=form,
        categories=categories,
        project_categories=project_categories,
        submit_button_text="Сохранить",
    )


@app.route("/project/edit/<int:project_id>", methods=["GET", "POST"])
@login_manager.unauthorized_handler
def project_edit_page_unauthorized():
    return redirect("/login")


@app.route("/category/<int:category_id>")
def category_page(category_id):
    db = db_session.create_session()
    category = db.query(Category).get(category_id)
    if category is None:
        flask.abort(404)
        return

    projects = get_projects_by_category(category_id)

    return render_template(
        'category.html',
        projects=projects,
        static_path=STATIC_PATH,
        title=category.name,
    )


@app.route("/category/recommended")
def category_recommended_page():
    projects = get_projects_recommended()

    return render_template(
        'category.html',
        projects=projects,
        static_path=STATIC_PATH,
        title="Рекомендовано вам",
    )


@app.route("/category/finish_line")
def category_finish_line_page():
    projects = get_projects_finish_line()

    return render_template(
        'category.html',
        projects=projects,
        static_path=STATIC_PATH,
        title="Финишная прямая",
    )


@app.route("/category/newly_created")
def category_newly_created_page():
    projects = get_projects_newly_created()

    return render_template(
        'category.html',
        projects=projects,
        static_path=STATIC_PATH,
        title="Новые проекты",
    )


@app.route("/category/all")
def category_all_page():
    projects = get_projects_all(20)

    return render_template(
        'category.html',
        projects=projects,
        static_path=STATIC_PATH,
        title="Все проекты",
    )


@app.route("/category/user_projects/<int:user_id>")
def my_projects_page(user_id):
    db = db_session.create_session()
    user = db.query(User).get(user_id)
    if not user:
        flask.abort(404)
        return

    projects = get_projects_by_author(user_id)

    return render_template(
        'category.html',
        projects=projects,
        static_path=STATIC_PATH,
        title=f"Проекты пользователя {user.login}"
    )


@app.route("/user_account/<int:user_id>")
def user_account_page(user_id):
    db = db_session.create_session()
    user = db.query(User).get(user_id)
    if user is None:
        flask.abort(404)
        return

    return render_template(
        'personal-account.html',
        static_path=STATIC_PATH,
        user=user,
    )


if __name__ == '__main__':
    main()
