import sys
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.main import bp
from app.main.forms import (AddCategoryForm, AddTaskForm, AddUserCategoryForm, EditProfileForm,
                            NewSessionAddTaskForm, SessionForm)
from app.models import Category, Task, User, UserCategory, UserSchema
from app.session import Session


USER_SCHEMA = UserSchema(exclude=("last_seen", ))


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# TODO: update to something relevant
@bp.route('/')
@bp.route('/index')
@login_required
def index():
    flash(f'Entered /index')
    user = User.query.filter_by(username=current_user.username).first_or_404()
    duser = get_dumped_user(user)

    return render_template('index.html', user=duser)


@bp.route('/user/<username>', methods=['GET'])
@login_required
def user(username):
    flash(f'Entered /user/{username}')

    user = User.query.filter_by(username=username).first_or_404()
    duser = get_dumped_user(user)

    result_list = (db.session.query(UserCategory, Category)
                    .filter(UserCategory.user_id == user.id)
                    .filter(Category.id == UserCategory.category_id)
                    .all())
    flash(f'{result_list}')

    user_task_list = Task.query.filter(Task.user_id == user.id).all()
    flash(f'{user_task_list}')

    return render_template('user.html', user=duser, result_list=result_list,
                                        user_task_list=user_task_list)


@bp.route('/user/<username>/new_session', methods=['GET'])
@login_required
def new_session(username, session_task_list):
    flash(f'Entered /user/{username}/new_session')

    user = User.query.filter_by(username=current_user.username).first_or_404()
    duser = get_dumped_user(user)

    if session_task_list is None or not session_task_list:
        session_task_list = []

    user_tasks = Task.query.filter(Task.user_id == user.id).all()
    flash(f'{user_tasks}')

    new_session_add_task_form = NewSessionAddTaskForm()
    new_session_add_task_form.task_id.choices = [(task.id, task.title) for task in user_tasks]
    if new_session_add_task_form.new_session_add_task_submit.data and new_session_add_task_form.validate_on_submit():
        task = Task.query.get(int(new_session_add_task_form.task_id.data))
        session_task_list.append(task)

        user_tasks = Task.query.filter(Task.user_id == user.id).all()
        
        new_session_add_task_form = NewSessionAddTaskForm()
        new_session_add_task_form.task_id.choices = [(task.id, task.title) for task in user_tasks]
        return render_template(url_for('main.new_session', username=current_user.username, session_task_list=session_task_list))
    return render_template('new_session.html', username=current_user.username, session_task_list=session_task_list,
                                    new_session_add_task_form=new_session_add_task_form)


@bp.route('/user/<username>/add_category', methods=['GET', 'POST'])
@login_required
def add_user_category(username):
    user = User.query.filter_by(username=username).first_or_404()
    duser = get_dumped_user(user)

    user_cat_id_list = []
    for user_cat in user.user_category:
        user_cat_id_list.append(user_cat.category_id)
    flash(f'{user_cat_id_list}')


    categories = Category.query.filter(Category.id.notin_(user_cat_id_list)).all()
    flash(f'{categories}')

    add_user_category_form = AddUserCategoryForm()
    add_user_category_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    if add_user_category_form.add_user_category_submit.data and add_user_category_form.validate_on_submit():
        user_category = UserCategory(user_id=user.id, category_id=add_user_category_form.category_id.data, 
                                     level=1, xp=0)
        db.session.add(user_category)
        db.session.commit()

        return redirect(url_for('main.user', username=current_user.username))
    return render_template('add_user_category.html', user=user, add_user_category_form=add_user_category_form)

@bp.route('/user/<username>/add_task', methods=['GET', 'POST'])
@login_required
def add_user_task(username):
    user = User.query.filter_by(username=username).first_or_404()
    duser = get_dumped_user(user)

    user_cat_id_list = []
    for user_cat in user.user_category:
        user_cat_id_list.append(user_cat.category_id)
    flash(f'{user_cat_id_list}')

    categories = Category.query.filter(Category.id.in_(user_cat_id_list)).all()
    flash(f'{categories}')

    add_task_form = AddTaskForm()
    add_task_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    if add_task_form.add_task_submit.data and add_task_form.validate_on_submit():
        # category = Category.query.get(int(add_task_form.category_id.data))
        # flash(f'{category}')

        task = Task(user_id=user.id,
                    category_id=add_task_form.category_id.data,
                    title=add_task_form.title.data, 
                    description=add_task_form.description.data, 
                    xp=add_task_form.xp.data)
        db.session.add(task)
        db.session.commit()

        return redirect(url_for('main.user', username=current_user.username))
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

# @bp.route('/follow/<username>')
# @login_required
# def follow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User {} not found.'.format(username))
#         return redirect(url_for('main.index'))
#     if user == current_user:
#         flash('You cannot follow yourself!')
#         return redirect(url_for('main.user', username=username))
#     current_user.follow(user)
#     db.session.commit()
#     flash('You are following {}!'.format(username))
#     return redirect(url_for('main.user', username=username))

# @bp.route('/unfollow/<username>')
# @login_required
# def unfollow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User {} not found.'.format(username))
#         return redirect(url_for('main.index'))
#     if user == current_user:
#         flash('You cannot unfollow yourself!')
#         return redirect(url_for('main.user', username=username))
#     current_user.unfollow(user)
#     db.session.commit()
#     flash('You are not following {}.'.format(username))
#     return redirect(url_for('main.user', username=username))

@bp.route('/session', methods=['GET', 'POST'])
def session():
    form = SessionForm()
    if form.validate_on_submit():
        flash('Generating Session: Session Length = {}, # of Categories = {}'.format(
            form.length_of_session.data, form.number_of_categories.data))

        categories = Category.query.all()
        session = Session(categories, form.length_of_session.data, form.number_of_categories.data)
        print(f'{session}', file=sys.stderr)
        return render_template('session2.html', title='Session', session=session)
    return render_template('session.html', title='Session', form=form)

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
    flash(f'dumped_user={dumped_user}')
    return dumped_user