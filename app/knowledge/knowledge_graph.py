from neo4j import GraphDatabase
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

class KnowledgeGraph:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_node(self, label: str, properties: Dict[str, Any]):
        with self.driver.session() as session:
            session.write_transaction(self._create_node, label, properties)

    def add_relationship(self, start_node: Dict[str, Any], end_node: Dict[str, Any], relationship_type: str, properties: Dict[str, Any] = {}):
        with self.driver.session() as session:
            session.write_transaction(self._create_relationship, start_node, end_node, relationship_type, properties)

    @staticmethod
    def _create_node(tx, label, properties):
        query = (
            f"CREATE (n:{label} $properties)"
        )
        tx.run(query, properties=properties)

    @staticmethod
    def _create_relationship(tx, start_node, end_node, relationship_type, properties):
        query = (
            f"MATCH (a:{start_node['label']} {{id: $start_id}}), "
            f"(b:{end_node['label']} {{id: $end_id}}) "
            f"CREATE (a)-[r:{relationship_type} $properties]->(b)"
        )
        tx.run(query, start_id=start_node['id'], end_id=end_node['id'], properties=properties)

class LearningEngine:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph

    async def learn(self, data: Dict[str, Any]):
        # Implement learning logic here
        # For example, extract entities and relationships from the data and add them to the knowledge graph
        entity = data.get("entity")
        if entity:
            self.knowledge_graph.add_node("Entity", {"id": entity["id"], "name": entity["name"]})
        
        relationship = data.get("relationship")
        if relationship:
            self.knowledge_graph.add_relationship(
                {"label": "Entity", "id": relationship["start_id"]},
                {"label": "Entity", "id": relationship["end_id"]},
                relationship["type"],
                {"weight": relationship.get("weight", 1.0)}
            )

class QueryEngine:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph

    async def query(self, query: str) -> List[Dict[str, Any]]:
        with self.knowledge_graph.driver.session() as session:
            result = session.read_transaction(self._run_query, query)
        return result

    @staticmethod
    def _run_query(tx, query):
        result = tx.run(query)
        return [record.data() for record in result]