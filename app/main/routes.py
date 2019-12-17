import math
import sys
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import (AddCategoryForm, AddTaskForm, AddUserCategoryForm,
                            EditProfileForm, NewSessionAddTaskForm,
                            RunSessionForm)
from app.models import (Category, Session, Task, TaskSchema, User,
                        UserCategory, UserSchema)

USER_SCHEMA = UserSchema(exclude=("last_seen", ))
TASKS_SCHEMA = TaskSchema(many=True, exclude=("timestamp", ))
DEBUG = False


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index', methods=['GET'])
@login_required
def index():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    duser = get_dumped_user(user)

    result_list = (db.session.query(UserCategory, Category)
                   .filter(UserCategory.user_id == user.id)
                   .filter(Category.id == UserCategory.category_id)
                   .all())

    user_task_list = Task.query.filter(Task.user_id == user.id).all()

    return render_template('index.html', user=duser, result_list=result_list,
                            user_task_list=user_task_list)


@bp.route('/user/<username>', methods=['GET'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    duser = get_dumped_user(user)

    result_list = (db.session.query(UserCategory, Category)
                   .filter(UserCategory.user_id == user.id)
                   .filter(Category.id == UserCategory.category_id)
                   .all())
    debug_flash("result_list", result_list)

    user_task_list = Task.query.filter(Task.user_id == user.id).all()
    return render_template('user.html', user=duser, result_list=result_list,
                            user_task_list=user_task_list)


@bp.route('/user/<username>/new_session', methods=['GET', 'POST'])
@login_required
def new_session(username):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    duser = get_dumped_user(user)

    session_draft = get_session_draft(current_user.id)
    debug_flash("session_draft", session_draft)

    task_id_list = []
    for task in session_draft.tasks:
        task_id_list.append(task.id)

    user_tasks = Task.query.filter(Task.user_id == user.id, Task.id.notin_(task_id_list)).all()

    new_session_add_task_form = NewSessionAddTaskForm()
    new_session_add_task_form.task_id.choices = [(task.id, f'{task.title} | {task.xp} XP') for task in user_tasks]

    if new_session_add_task_form.new_session_add_task_submit.data and new_session_add_task_form.validate_on_submit():
        session_draft = get_session_draft(current_user.id)
        task = Task.query.get(int(new_session_add_task_form.task_id.data))

        session_draft.tasks.append(task)
        db.session.add(session_draft)
        db.session.commit()

        # TODO: possible candidate for removal, check if any session difference after commit
        session_draft = get_session_draft(current_user.id)

        task_id_list = []
        for task in session_draft.tasks:
            task_id_list.append(task.id)

        user_tasks = Task.query.filter(Task.user_id == user.id, Task.id.notin_(task_id_list)).all()

        new_session_add_task_form = NewSessionAddTaskForm()
        new_session_add_task_form.task_id.choices = [(task.id, f'{task.title} | {task.xp} XP') for task in user_tasks]

        return render_template('new_session.html', username=current_user.username, new_session_add_task_form=new_session_add_task_form, session_draft=session_draft)
    return render_template('new_session.html', username=current_user.username, new_session_add_task_form=new_session_add_task_form, session_draft=session_draft)


@bp.route('/user/<username>/run_session', methods=['GET', 'POST'])
@login_required
def run_session(username):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    duser = get_dumped_user(user)

    session_draft = get_session_draft(current_user.id)
    run_session_form = RunSessionForm(session_id=session_draft.id)
    # run_session_form.session_tasks.choices = [(task.id, task.title) for task in session_draft.tasks]

    if run_session_form.run_session_submit.data and run_session_form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first_or_404()
        duser = get_dumped_user(user)

        completed_task_ids = request.form.getlist("completed")

        for task_id in completed_task_ids:
            process_task(task_id, user)
        update_session(run_session_form.session_id.data)

        return redirect(url_for('main.index'))
    return render_template('run_session.html', session=session_draft, run_session_form=run_session_form)


@bp.route('/user/<username>/add_category', methods=['GET', 'POST'])
@login_required
def add_user_category(username):
    user = User.query.filter_by(username=username).first_or_404()
    duser = get_dumped_user(user)

    user_cat_id_list = []
    for user_cat in user.user_category:
        user_cat_id_list.append(user_cat.category_id)

    categories = Category.query.filter(Category.id.notin_(user_cat_id_list)).all()

    add_user_category_form = AddUserCategoryForm()
    add_user_category_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    if add_user_category_form.add_user_category_submit.data and add_user_category_form.validate_on_submit():
        user_category = UserCategory(user_id=user.id, category_id=add_user_category_form.category_id.data,
                                     level=1, xp=0, xp_to_next_level=5, level_up_xp_modifier=5)
        db.session.add(user_category)
        db.session.commit()
        flash(f'Category added for {current_user.username}')

        return redirect(url_for('main.add_user_category', username=current_user.username))
    return render_template('add_user_category.html', user=user, add_user_category_form=add_user_category_form)


@bp.route('/user/<username>/add_task', methods=['GET', 'POST'])
@login_required
def add_user_task(username):
    user = User.query.filter_by(username=username).first_or_404()
    duser = get_dumped_user(user)

    user_cat_id_list = []
    for user_cat in user.user_category:
        user_cat_id_list.append(user_cat.category_id)

    add_task_form = AddTaskForm()
    categories = Category.query.filter(Category.id.in_(user_cat_id_list)).all()
    add_task_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    if add_task_form.add_task_submit.data and add_task_form.validate_on_submit():
        task = Task(user_id=user.id,
                    category_id=add_task_form.category_id.data,
                    title=add_task_form.title.data,
                    description=add_task_form.description.data,
                    xp=add_task_form.xp.data)
        db.session.add(task)
        db.session.commit()
        flash(f'Task "{task.title}" added for {current_user.username}')

        return redirect(url_for('main.add_user_task', username=current_user.username))
    return render_template('add_task.html', user=user, add_task_form=add_task_form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/dbview', methods=['GET', 'POST'])
def db_view():
    users = User.query.all()
    categories = Category.query.order_by('title')

    add_category_form = AddCategoryForm()
    add_task_form = AddTaskForm()
    add_task_form.category_id.choices = [(cat.id, cat.title) for cat in categories]

    if add_category_form.add_category_submit.data and add_category_form.validate_on_submit():
        category = Category(title=add_category_form.title.data,
                            description=add_category_form.description.data)
        db.session.add(category)
        db.session.commit()

        add_category_form = AddCategoryForm()
        add_task_form = AddTaskForm()
        categories = Category.query.order_by('title')
        add_task_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
        return render_template('db_view.html', title='DB View', users=users, categories=categories, add_category_form=add_category_form, add_task_form=add_task_form)
    elif add_task_form.add_task_submit.data and add_task_form.validate_on_submit():
        flash(f'form={add_task_form}')
        flash(f'{add_task_form.category_id.data}')

        category = Category.query.get(int(add_task_form.category_id.data))
        flash(f'{category}')

        task = Task(title=add_task_form.title.data,
                    description=add_task_form.description.data,
                    category=category)
        db.session.add(task)
        db.session.commit()

        add_category_form = AddCategoryForm()
        add_task_form = AddTaskForm()
        categories = Category.query.order_by('title')
        add_task_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
        return render_template('db_view.html', title='DB View', users=users, categories=categories, add_category_form=add_category_form, add_task_form=add_task_form)
    return render_template('db_view.html', title='DB View', users=users, categories=categories, add_category_form=add_category_form, add_task_form=add_task_form)

# Utility Methods
# TODO: move to proper utility classes


def get_dumped_user(user):
    dumped_user = USER_SCHEMA.dump(user)
    # flash(f'dumped_user={dumped_user}')
    return dumped_user


def debug_flash(item_name, item):
    if DEBUG is True:
        flash(f'{item_name}={item}')

def get_session_draft(user_id):
    session_draft = Session.query.filter(Session.user_id == user_id, Session.is_draft.is_(True)).first()
    debug_flash("session_draft", session_draft)

    if session_draft:
        return session_draft
    else:
        session = Session(user_id=user_id, is_draft=True)
        db.session.add(session)
        db.session.commit()
        return session


def process_task(task_id, user):
    task = Task.query.get(int(task_id))
    category = Category.query.get(int(task.category_id))

    update_user_xp(user, task)
    update_user_category_xp(user, category, task)
    db.session.commit()

def update_user_xp(user, task):
    debug_flash("user on entry to update_user_xp", user)

    if task.xp < user.xp_to_next_level:
        user.xp = user.xp + task.xp
        user.xp_to_next_level = user.xp_to_next_level - task.xp
    elif task.xp >= user.xp_to_next_level:
        task_xp = task.xp

        while task_xp >= user.xp_to_next_level:
            # Update User
            user.level = user.level + 1
            user.xp = user.xp + task_xp

            task_xp = task_xp - user.xp_to_next_level
            user.xp_to_next_level_constant = (user.level_up_xp_modifier * .01 + 1) * user.xp_to_next_level_constant
            user.xp_to_next_level = int(math.ceil(user.xp_to_next_level_constant))

        # Account for task_xp remainder
        user.xp = user.xp + task_xp
        user.xp_to_next_level = user.xp_to_next_level - task_xp

    debug_flash("user on exit of update_user_xp", user)


def update_user_category_xp(user, category, task):
    debug_flash("user on entry to update_user_category_xp", user)
    user_category = UserCategory.query.filter(UserCategory.user_id == user.id, UserCategory.category_id == category.id).first()

    if task.xp < user_category.xp_to_next_level:
        user_category.xp = user_category.xp + task.xp
        user_category.xp_to_next_level = user_category.xp_to_next_level - task.xp

    elif task.xp >= user_category.xp_to_next_level:
        task_xp = task.xp

        while task_xp >= user_category.xp_to_next_level:
            user_category.level = user_category.level + 1
            user_category.xp = user_category.xp + task_xp

            task_xp = task_xp - user_category.xp_to_next_level
            user_category.xp_to_next_level_constant = (user_category.level_up_xp_modifier * .01 + 1) * user_category.xp_to_next_level_constant
            user_category.xp_to_next_level = int(math.ceil(user_category.xp_to_next_level_constant))

        # Account for task_xp remainder
        user_category.xp = user_category.xp + task_xp
        user_category.xp_to_next_level = user_category.xp_to_next_level - task_xp

    debug_flash("user on exit of update_user_category_xp", user)


def update_session(session_id):
    session = Session.query.get(int(session_id))
    session.is_draft = False
    session.completed = datetime.now()
    db.session.commit()
