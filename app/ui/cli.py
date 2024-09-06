import click
import requests
import json

BASE_URL = "http://localhost:8000"

def handle_api_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            click.echo(f"Error: {str(e)}", err=True)
    return wrapper

@click.group()
def cli():
    """Command-line interface for the Advanced LLM-based Agent System"""
    pass

@cli.command()
@click.argument('project_name')
@handle_api_error
def create_project(project_name):
    """Create a new project"""
    response = requests.post(f"{BASE_URL}/projects", params={"project_name": project_name})
    response.raise_for_status()
    click.echo(response.json()["message"])

@cli.command()
@click.argument('project_name')
@handle_api_error
def project_status(project_name):
    """Get the status of a project"""
    response = requests.get(f"{BASE_URL}/projects/{project_name}/status")
    click.echo(json.dumps(response.json(), indent=2))

@cli.command()
@click.argument('project_name')
@click.argument('commit_message')
@handle_api_error
def commit(project_name, commit_message):
    """Commit changes in a project"""
    response = requests.post(f"{BASE_URL}/projects/{project_name}/commit", params={"commit_message": commit_message})
    response.raise_for_status()
    click.echo(response.json()["message"])

@cli.command()
@click.argument('project_name')
@click.argument('branch_name')
@handle_api_error
def create_branch(project_name, branch_name):
    """Create a new branch in a project"""
    response = requests.post(f"{BASE_URL}/projects/{project_name}/branch", params={"branch_name": branch_name})
    response.raise_for_status()
    click.echo(response.json()["message"])

@cli.command()
@click.argument('project_name')
@click.argument('branch_name')
@handle_api_error
def switch_branch(project_name, branch_name):
    """Switch to a different branch in a project"""
    response = requests.post(f"{BASE_URL}/projects/{project_name}/switch_branch", params={"branch_name": branch_name})
    response.raise_for_status()
    click.echo(response.json()["message"])

@cli.command()
@click.argument('text')
@handle_api_error
def process_nl(text):
    """Process natural language input"""
    response = requests.post(f"{BASE_URL}/process_natural_language", params={"text": text})
    response.raise_for_status()
    click.echo(response.json()["response"])

if __name__ == '__main__':
    cli()