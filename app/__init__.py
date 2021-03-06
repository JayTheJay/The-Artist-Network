from flask import Flask, render_template, flash, url_for, redirect, request, session
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_app(config_name):
    app = Flask(__name__)
    config_name = 'default'
    app.config.from_object(config[config_name])
    app.secret_key = 'MarcysiaJestMistrzemProgramowania'
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    from app import models
    from app.forms import LoginForm, RegistrationForm, EditProfileForm
    from app.models import Artist, login
    login.init_app(app)


    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('base.html')
        
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = Artist.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        return render_template('login.html', title='Sign In', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = Artist(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route('/user/<username>')
    @login_required
    def user(username):
        user = Artist.query.filter_by(username=username).first_or_404()
        posts = [
            {'author': user, 'body': 'Test post #1'},
            {'author': user, 'body': 'Test post #2'}
        ]
        return render_template('user.html', user=user)

    

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = EditProfileForm(current_user.username)
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.aboutMe = form.about_me.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit_profile'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.about_me.data = current_user.aboutMe
        return render_template('edit_profile.html', title='Edit Profile',
                               form=form)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                               backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('Microblog startup')
    

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', username=current_user.username)

    @app.route('/musicgroups')
    @login_required
    def musicgroups():
        return render_template('musicgroups.html', username=current_user.username)

    @app.route('/artists')
    @login_required
    def artists():
        return render_template('artists.html', username=current_user.username)

    @app.route('/roles')
    @login_required
    def roles():
        return render_template('roles.html', username=current_user.username)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        if session.get('was_once_logged_in'):
            # prevent flashing automatically logged out message
            del session['was_once_logged_in']
        flash('You have successfully logged yourself out.')
        return redirect('/login')

    return app


