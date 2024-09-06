import click
import requests
import json

BASE_URL = "http://localhost:8000"

@click.group()
def cli():
    """Command-line interface for the Advanced LLM-based Agent System"""
    pass

@cli.command()
@click.argument('project_name')
def create_project(project_name):
    """Create a new project"""
    response = requests.post(f"{BASE_URL}/projects", params={"project_name": project_name})
    click.echo(response.json()["message"])

@cli.command()
@click.argument('project_name')
def project_status(project_name):
    """Get the status of a project"""
    response = requests.get(f"{BASE_URL}/projects/{project_name}/status")
    click.echo(json.dumps(response.json(), indent=2))

@cli.command()
@click.argument('project_name')
@click.argument('commit_message')
def commit(project_name, commit_message):
    """Commit changes in a project"""
    response = requests.post(f"{BASE_URL}/projects/{project_name}/commit", params={"commit_message": commit_message})
    click.echo(response.json()["message"])

@cli.command()
@click.argument('project_name')
@click.argument('branch_name')
def create_branch(project_name, branch_name):
    """Create a new branch in a project"""
    response = requests.post(f"{BASE_URL}/projects/{project_name}/branch", params={"branch_name": branch_name})
    click.echo(response.json()["message"])

@cli.command()
@click.argument('project_name')
@click.argument('branch_name')
def switch_branch(project_name, branch_name):
    """Switch to a different branch in a project"""
    response = requests.post(f"{BASE_URL}/projects/{project_name}/switch_branch", params={"branch_name": branch_name})
    click.echo(response.json()["message"])

@cli.command()
@click.argument('text')
def process_nl(text):
    """Process natural language input"""
    response = requests.post(f"{BASE_URL}/process_natural_language", params={"text": text})
    click.echo(response.json()["response"])

if __name__ == '__main__':
    cli()