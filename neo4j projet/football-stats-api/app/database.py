from neo4j import GraphDatabase
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "")
        self.driver = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            print("✅ Connected to Neo4j successfully")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()
            print("Neo4j connection closed")

    def execute_query(self, query: str, parameters: dict = None):
        """Execute a Cypher query and return results"""
        database = os.getenv("NEO4J_DATABASE", "neo4j")
        with self.driver.session(database=database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: dict = None):
        """Execute a write transaction"""
        database = os.getenv("NEO4J_DATABASE", "neo4j")
        with self.driver.session(database=database) as session:
            result = session.write_transaction(
                lambda tx: tx.run(query, parameters or {})
            )
            return result


# Global connection instance
neo4j_conn = Neo4jConnection()