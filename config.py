import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Provide the necessary arguments for KnowledgeGraph initialization
uri = os.getenv("NEO4J_URI")  # This should be the URI
user = os.getenv("NEO4J_USER")  # Your Neo4j username
password = os.getenv("NEO4J_PASSWORD")  # Your Neo4j password
base_path = os.getenv("VIRTUAL_ENV_BASE_PATH", "./virtual_env")  # Default to './virtual_env' if not set