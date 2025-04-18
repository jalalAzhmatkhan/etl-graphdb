from neo4j import GraphDatabase, Query

from settings import settings

class Neo4jService:
    """
    Service for Neo4j
    """
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            f"bolt://{settings.NEO4J_HOST}:{settings.NEO4J_PORT}",
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def clear_database(self, db_name: str):
        """
        A function to clear all nodes and relationships
        :param db_name:
        :return:
        """
        with self.neo4j_driver.session(database=db_name) as session:
            session.run(f"MATCH (n) DETACH DELETE n")
            print(f"[Neo4jService] Database '{db_name}' cleared.")

    def create_database_if_not_exists(self, db_name: str):
        """
        A function to create a Neo4j DB if the db_name does not exist.
        :param db_name:
        :return:
        """
        with self.neo4j_driver.session() as session:
            result = session.run("SHOW DATABASES")
            db_names = [record["name"] for record in result]

            if db_name not in db_names:
                query = Query("CREATE DATABASE $db_name")
                session.run(query)
                print(f"Database '{db_name}' created.")
            else:
                print(f"[Neo4jService] Database '{db_name}' already exists.")

    def close_connection(self):
        """
        Close the connection to Neo4j
        :return:
        """
        self.neo4j_driver.close()
        print("[Neo4jService] Session closed.")

neo4j_service = Neo4jService()
