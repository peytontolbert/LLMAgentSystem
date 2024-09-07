import os
import shutil
import requests

PYTHON_TEMPLATE = """
import json

context = json.loads('''
{context}
''')

def execute_user_code():
    {user_code}

result = execute_user_code()
print(json.dumps({{"result": result}}))
"""

JAVASCRIPT_TEMPLATE = """
const context = JSON.parse(`
{context}
`);

function executeUserCode() {{
    {user_code}
}}

const result = executeUserCode();
console.log(JSON.stringify({{ result }}));
"""

BASH_TEMPLATE = """
context='{context}'

{user_code}

echo "{{\"result\": \"$result\"}}"
"""

def get_tool_template(language: str) -> str:
    if language == 'python':
        return PYTHON_TEMPLATE
    elif language == 'javascript':
        return JAVASCRIPT_TEMPLATE
    elif language == 'bash':
        return BASH_TEMPLATE
    else:
        raise ValueError(f"Unsupported language: {language}")

async def create_file_template(context):
    try:
        file_path = os.path.join(context['workspace'], context['step']['file_name'])
        with open(file_path, 'w') as f:
            f.write(context['step']['content'])
        context['logger'].info(f"Created file: {file_path}")
        return {"success": True, "file_path": file_path}
    except Exception as e:
        context['logger'].error(f"Error creating file: {str(e)}")
        return {"error": str(e)}

async def copy_directory_template(context):
    try:
        src = context['step']['source_path']
        dst = os.path.join(context['workspace'], context['step']['destination_path'])
        shutil.copytree(src, dst)
        context['logger'].info(f"Copied directory from {src} to {dst}")
        return {"success": True, "source": src, "destination": dst}
    except Exception as e:
        context['logger'].error(f"Error copying directory: {str(e)}")
        return {"error": str(e)}

async def connect_api_template(context):
    try:
        response = requests.get(context['step']['api_url'], headers=context['step'].get('headers', {}))
        response.raise_for_status()
        context['logger'].info(f"Successfully connected to API: {context['step']['api_url']}")
        return {"success": True, "status_code": response.status_code, "content": response.json()}
    except Exception as e:
        context['logger'].error(f"Error connecting to API: {str(e)}")
        return {"error": str(e)}