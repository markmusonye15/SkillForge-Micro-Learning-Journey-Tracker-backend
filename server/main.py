import os
import typer
from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from .config import config
from .models import db, bcrypt
from .models.user import User
from .models.journey import Journey
from .models.step import Step

cli = typer.Typer(help="SkillForge CLI: A tool for managing the application's data from the command line.")

# --- Health Check Blueprint ---
health_bp = Blueprint('health_bp', __name__)
@health_bp.route('/health')
def health_check():
    """Provides a simple health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'SkillForge API is running'}), 200

# --- App Factory ---
def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # Register the health check blueprint
    app.register_blueprint(health_bp)

    # You will register your other API blueprints here later
    # from .routes import auth_routes
    # app.register_blueprint(auth_routes.bp)
    
    return app

# --- CLI Commands (No changes needed below this line) ---

@cli.command()
def init_db():
    """Initializes the database by creating all tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        typer.secho('Database initialized successfully!', fg=typer.colors.GREEN)

@cli.command()
def drop_db():
    """Drops all database tables. This is a destructive operation."""
    if typer.confirm('Are you sure you want to drop all tables?'):
        app = create_app()
        with app.app_context():
            db.drop_all()
            typer.secho('Database tables dropped!', fg=typer.colors.RED)

@cli.command()
def create_user(
    username: str = typer.Argument(..., help="Username for the new user."),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password for the new user.")
):
    """Creates a new user in the database."""
    app = create_app()
    with app.app_context():
        if User.query.filter_by(username=username).first():
            typer.secho(f'User "{username}" already exists!', fg=typer.colors.YELLOW)
            raise typer.Exit(1)
        
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        typer.secho(f'User "{username}" created successfully!', fg=typer.colors.GREEN)

@cli.command()
def list_users():
    """Lists all registered users."""
    app = create_app()
    with app.app_context():
        users = User.query.all()
        if not users:
            typer.echo('No users found.')
            return
        
        typer.secho('Registered Users:', bold=True)
        for user in users:
            typer.echo(f'  ID: {user.id}, Username: {user.username}')

@cli.command()
def delete_user(user_id: int = typer.Argument(..., help="The ID of the user to delete.")):
    """Deletes a user and all their associated data."""
    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            typer.secho(f"Error: User with ID {user_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)

        if typer.confirm(f"Are you sure you want to delete user '{user.username}'? This will delete all their journeys and steps."):
            db.session.delete(user)
            db.session.commit()
            typer.secho(f"User '{user.username}' deleted successfully.", fg=typer.colors.GREEN)

@cli.command()
def create_journey(user_id: int, title: str):
    """Creates a new learning journey for a user."""
    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            typer.secho(f"Error: User with ID {user_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        journey = Journey(title=title, user_id=user.id)
        db.session.add(journey)
        db.session.commit()
        typer.secho(f"Journey '{title}' created for user '{user.username}'!", fg=typer.colors.GREEN)

@cli.command()
def update_journey(journey_id: int, new_title: str):
    """Updates the title of a journey."""
    app = create_app()
    with app.app_context():
        journey = Journey.query.get(journey_id)
        if not journey:
            typer.secho(f"Error: Journey with ID {journey_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        journey.title = new_title
        db.session.commit()
        typer.secho(f"Journey {journey_id} updated to '{new_title}'.", fg=typer.colors.GREEN)

@cli.command()
def delete_journey(journey_id: int):
    """Deletes a journey and all its steps."""
    app = create_app()
    with app.app_context():
        journey = Journey.query.get(journey_id)
        if not journey:
            typer.secho(f"Error: Journey with ID {journey_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        db.session.delete(journey)
        db.session.commit()
        typer.secho(f"Journey '{journey.title}' deleted successfully.", fg=typer.colors.GREEN)

@cli.command()
def list_journeys(user_id: int):
    """Lists all learning journeys for a specific user."""
    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            typer.secho(f"Error: User with ID {user_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        if not user.journeys:
            typer.echo(f"No journeys found for user '{user.username}'.")
            return
        typer.secho(f"Journeys for {user.username}:", bold=True)
        for journey in user.journeys:
            typer.echo(f"  ID: {journey.id}, Title: '{journey.title}'")

@cli.command()
def create_step(journey_id: int, title: str):
    """Creates a new step within a journey."""
    app = create_app()
    with app.app_context():
        journey = Journey.query.get(journey_id)
        if not journey:
            typer.secho(f"Error: Journey with ID {journey_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        step = Step(title=title, journey_id=journey_id)
        db.session.add(step)
        db.session.commit()
        typer.secho(f"Step '{title}' added to journey '{journey.title}'!", fg=typer.colors.GREEN)

@cli.command()
def update_step(step_id: int, new_title: str):
    """Updates the title of a step."""
    app = create_app()
    with app.app_context():
        step = Step.query.get(step_id)
        if not step:
            typer.secho(f"Error: Step with ID {step_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        step.title = new_title
        db.session.commit()
        typer.secho(f"Step {step_id} updated to '{new_title}'.", fg=typer.colors.GREEN)

@cli.command()
def delete_step(step_id: int):
    """Deletes a single step."""
    app = create_app()
    with app.app_context():
        step = Step.query.get(step_id)
        if not step:
            typer.secho(f"Error: Step with ID {step_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        db.session.delete(step)
        db.session.commit()
        typer.secho(f"Step '{step.title}' deleted successfully.", fg=typer.colors.GREEN)

@cli.command()
def list_steps(journey_id: int):
    """Lists all steps for a specific journey."""
    app = create_app()
    with app.app_context():
        journey = Journey.query.get(journey_id)
        if not journey:
            typer.secho(f"Error: Journey with ID {journey_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        if not journey.steps.all():
            typer.echo(f"No steps found for journey '{journey.title}'.")
            return
        typer.secho(f"Steps for '{journey.title}':", bold=True)
        for step in journey.steps:
            status = "✅" if step.is_complete else "❌"
            typer.echo(f"  {status} ID: {step.id}, Title: '{step.title}'")

@cli.command()
def complete_step(step_id: int):
    """Marks a step as complete."""
    app = create_app()
    with app.app_context():
        step = Step.query.get(step_id)
        if not step:
            typer.secho(f"Error: Step with ID {step_id} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
        step.is_complete = True
        db.session.commit()
        typer.secho(f"Step '{step.title}' marked as complete!", fg=typer.colors.GREEN)

@cli.command()
def run_server(
    host: str = typer.Option("127.0.0.1", help="Host to run the server on"),
    port: int = typer.Option(5000, help="Port to run the server on"),
    debug: bool = typer.Option(True, help="Enable debug mode")
):
    """Runs the Flask development server."""
    app = create_app('development' if debug else 'production')
    app.run(host=host, port=port)

# This part is only for Typer to run the CLI commands
if __name__ == '__main__':
    cli()
