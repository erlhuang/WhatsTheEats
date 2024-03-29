from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ListingForm, ItemForm, AutomateForm
from app.models import User, Listing, Item
from app.auth.email import send_password_reset_email
from app.main.menucrawler import crawlmenu
import json
import requests

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) #if already logged in then go to home
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() #match user
        if user is None or not user.check_password(form.password.data):
            #Either user doesnt exist or pw doesnt match
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        #if not, we can log in
        login_user(user, remember=form.remember_me.data)
        #goes to the page we were on previously before login
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index') #if there wasn't one go to home
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: #already logged in
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, you are registered! Please log in!')
        return redirect(url_for('auth.login')) #after registration redirect to login
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index')) #Loggedin users shouldnt be able to access
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Reset password instructions have been sent to your email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/admin', methods=['GET', 'POST'])
def addListing():
    if current_user.username != 'soupercell':
        return redirect(url_for('main.index'))
    else:
        # print('poop')
        form = ListingForm()
        if form.validate_on_submit():
            newListing = Listing(title=form.title.data, imageurl=form.imageurl.data, \
            weekdayHrs=form.timeopen.data, weekendHrs=form.timeopen2.data, \
            description=form.addedInfo.data, upvotes=0, downvotes=0, \
            acronym=form.acronym.data, restaurant=form.isRestaurant.data)
            db.session.add(newListing)
            db.session.commit()
            flash('Listing added.')
            return redirect(url_for('main.dining'))
        return render_template('auth/admin.html', form=form)

@bp.route('/admin/<listing>', methods=['GET', 'POST'])
def addItem(listing):
    # if current_user.username != 'soupercell':
    #     return redirect(url_for('main.index'))
    # else:
    #     form = ItemForm()
    #     if form.validate_on_submit():
    #         list = Listing.query.filter_by(acronym=listing).first_or_404()
    #         newItem = Item(title=form.title.data, acronym=form.acronym.data, \
    #         imageurl=form.imageurl.data, nutritionURL=form.itemURL.data)
    #         db.session.add(newItem)
    #         list.menu_items.append(newItem)
    #         db.session.commit()
    #         flash('Item added.')
    #         return redirect(url_for('main.dining'))
    #     return render_template('auth/admin.html', form=form)
    if current_user.username != 'soupercell':
        return redirect(url_for('main.index'))
    else:
        form = AutomateForm()
        if form.validate_on_submit():
            crawlmenu()
        return render_template('auth/admin.html', form=form)
