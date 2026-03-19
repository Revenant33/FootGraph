# app/database.py
from neo4j import GraphDatabase
from app.config import settings

class Neo4jConnection:
    def __init__(self):
        self.driver = None
        
    def connect(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
    def close(self):
        if self.driver:
            self.driver.close()
            
    def get_session(self):
        return self.driver.session()
    
    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# Instance globale
neo4j_conn = Neo4jConnection()