import sys
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.main import bp
from app.main.forms import (AddCategoryForm, AddTaskForm, AddUserCategoryForm, EditProfileForm,
                            SessionForm)
from app.models import Category, Task, User, UserCategoryXp
from app.session import Session


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# TODO: update to something relevant
@bp.route('/')
@bp.route('/index')
@login_required
def index(username):
    flash(f'Entered index')
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('index.html', user=user)


@bp.route('/user/<username>')
@login_required
def user(username):
    flash(f'{username}')
    user = User.query.filter_by(username=username).first_or_404()
    flash(f'{user}')
    categories = []
    tasks = []
    # user_cat_xps, categories, tasks = (db.session.query(UserCategoryXp, Category, Task)
    #                 .filter(UserCategoryXp.user_id == user.id)
    #                 .filter(Category.id == UserCategoryXp.category_id)
    #                 .filter(Task.user_id == user.id)
    #                 .all())
    # flash(f'{categories, tasks}')

    return render_template('user.html', title='User Profile', user=user, categories=categories, tasks=tasks)

@bp.route('/user/<username>/add_task', methods=['GET', 'POST'])
@login_required
def add_user_task(username):
    user = User.query.filter_by(username=username).first_or_404()

    query_tuple = (db.session.query(UserCategoryXp, Category, Task)
                    .filter(UserCategoryXp.user_id == user.id)
                    .filter(Category.id == UserCategoryXp.category_id)
                    .all())
    flash(f'{query_tuple}')

    add_task_form = AddTaskForm()
    add_task_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    if add_task_form.add_task_submit.data and add_task_form.validate_on_submit():
        #category = Category.query.get(int(add_task_form.category_id.data))
        # flash(f'{category}')

        # task = Task(title=add_task_form.title.data, 
        #             description=add_task_form.description.data, 
        #             category=category)
        # db.session.add(task)
        # db.session.commit()

        add_category_form = AddCategoryForm()
        add_task_form = AddTaskForm()
        categories = Category.query.order_by('title')
        add_task_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
        return render_template('add_task.html', user=user, add_task_form=add_task_form)
    return render_template('add_task.html', user=user, add_task_form=add_task_form)


@bp.route('/user/<username>/add_category', methods=['GET', 'POST'])
@login_required
def add_user_category(username):
    user = User.query.filter_by(username=username).first_or_404()
    categories = Category.query.order_by('title')

    add_user_category_form = AddUserCategoryForm()
    add_user_category_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    if add_user_category_form.add_category_submit.data and add_user_category_form.validate_on_submit():
        user_category_xp = UserCategoryXp(user_id=user.id, 
                            category_id=add_user_category_form.description.data, user_category_points=0)
        db.session.add(user_category_xp)
        db.session.commit()

        categories = Category.query.order_by('title')
        add_category_form = AddUserCategoryForm()
        add_user_category_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
        return render_template('add_user_category.html', user=user, add_user_category_form=add_user_category_form)
    return render_template('add_user_category.html', user=user, add_user_category_form=add_user_category_form)



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
