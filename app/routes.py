from flask import Blueprint, render_template, request, redirect, url_for, flash
# We need or_ for the database search logic
from sqlalchemy import or_
from unicodedata import category
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

# Import models and forms from the local app package
from . import db, User, Portfolio
from .forms import LoginForm, RegistrationForm, ProjectForm

# Define the Blueprint instance (Simplified for reliable static/template handling)
main = Blueprint('main', __name__, template_folder='../templates')


# --- GENERAL ROUTES (READ) ---
# app/routes.py

@main.route('/')
def index():
    search_query = request.args.get('search')
    category_filter = request.args.get('category')  # NEW: Get the category filter

    # Start with a base query object
    query = Portfolio.query

    # 1. Apply Search Filter (Title OR Description)
    if search_query:
        query = query.filter(
            or_(
                Portfolio.title.ilike(f'%{search_query}%'),
                Portfolio.description.ilike(f'%{search_query}%')
            )
        )

    # 2. Apply Category Filter (AND logic)
    if category_filter:
        query = query.filter(Portfolio.category == category_filter)  # Exact match required

    # Execute the final combined query
    projects_to_display = query.all()

    return render_template('index.html',
                           portfolio_projects=projects_to_display,
                           title='Home')


@main.route('/about')
def about():
    return render_template('about.html', title='About Me')


# --- AUTHENTICATION ROUTES (CREATE, READ, DELETE) ---

@main.route('/register', methods=['GET', 'POST'])
def register():
    # Instantiate the secure form
    form = RegistrationForm()

    # Validate on POST request
    if form.validate_on_submit():
        name = form.full_name.data
        email = form.email_address.data
        password = form.password.data

        # CRITICAL: HASH THE PASSWORD
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user = User(full_name=name, email_address=email, password=hashed_password)

        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Thanks {name}, you are now registered! Please log in.', 'success')
            return redirect(url_for('main.login'))

        except:
            db.session.rollback()
            flash('Error: That email address may already be registered.', 'error')

    # Render form for GET or failed POST
    return render_template('register.html', title='Register', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email_address.data
        password = form.password.data

        user = User.query.filter_by(email_address=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')

            # Redirect to the page the user tried to access, or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Error: Invalid email or password', 'danger')

    return render_template('login.html', title='Login', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# --- ADMIN (CRUD) ROUTES ---
@main.route('/admin/add_project', methods=['GET', 'POST'])
@login_required
def admin_add_project():
    form = ProjectForm()

    if form.validate_on_submit():
        # 1. Object Creation
        new_project = Portfolio(title=form.title.data,
                                description=form.description.data,
                                link=form.link.data)
        try:
            # 2. Database Commit
            db.session.add(new_project)
            db.session.commit()  # <--- CRITICAL STEP

            flash(f"Project '{form.title.data}' added successfully!", 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            # 3. Error Handling
            db.session.rollback()
            print(f"Database Error: {e}")  # Check the terminal for this output!
            flash('Error adding project. Check server logs.', 'error')

    return render_template('index.html', title='Add Project', form=form)


@main.route('/admin/edit_project/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_project(id):
    # Retrieve the project object FIRST
    project_to_edit = Portfolio.query.get_or_404(id)

    # Pre-populate the form with existing data
    form = ProjectForm(obj=project_to_edit)

    if form.validate_on_submit():
        # Update the tracked object with the new form data
        project_to_edit.title = form.title.data
        project_to_edit.description = form.description.data
        project_to_edit.link = form.link.data

        # Save the changes to the database
        db.session.commit()

        flash(f"Project '{project_to_edit.title}' updated successfully!", 'success')
        return redirect(url_for('main.index'))

    # Render the template for both GET and failed POST
    return render_template('edit_project.html',
                           title=f"Edit {project_to_edit.title}",
                           form=form)


@main.route('/admin/delete_project/<int:id>', methods=['POST'])
@login_required
def admin_delete_project(id):
    project_to_delete = Portfolio.query.get_or_404(id)

    # Delete the project and commit the change
    db.session.delete(project_to_delete)
    db.session.commit()

    flash(f'Project {project_to_delete.title} has been deleted!', 'success')
    return redirect(url_for('main.index'))