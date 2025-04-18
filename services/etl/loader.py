from typing import Optional

import dask.bag as db
import pandas as pd

from services.graphdb import neo4j_service
from settings import settings

class LoaderService:
    """
    A service to load the data to a Graph DB
    """
    def __init__(self):
        """
        Init function
        """
        self.driver = neo4j_service.neo4j_driver

    def create_nodes_and_relationships(self, tx, row):
        """
        Create a Neo4j nodes and its relationships
        :param tx:
        :param row:
        :return:
        """
        nomenclature = row['nomenclature_naming']
        object_name = row['object_name']
        serving_area = row['Serving Area']
        location = row['Location']
        zone = row['Zone']

        # Create Nomenclature node
        tx.run("""
            MERGE (n:Nomenclature {name: $nomenclature})
        """, nomenclature=nomenclature)

        # Create Sensor Object node and HAS_SENSOR relationship
        tx.run("""
            MERGE (s:SensorObject {name: $object_name})
            SET s.description = $description,
                s.upper_limit = $upper_limit,
                s.lower_limit = $lower_limit,
                s.value_type = $object_type,
                s.units = $units
            MERGE (n:Nomenclature {name: $nomenclature})-[:HAS_SENSOR]->(s)
        """, nomenclature=nomenclature, object_name=object_name,
       description=row['object_description'],
       upper_limit=row['upper_limit'],
       lower_limit=row['lower_limit'],
       object_type=row['object_type'],
       units=row['units'])

        # Create FEEDS relationships based on layers
        if row['found_in_col'] == '1st Layer':
            if pd.notna(row['2nd Layer']) and row['2nd Layer']:
                tx.run("""
                    MERGE (n1:Nomenclature {name: $n1})
                    MERGE (n2:Nomenclature {name: $n2})
                    MERGE (n1)-[:FEEDS]->(n2)
                """, n1=nomenclature, n2=row['2nd Layer'])
                if pd.notna(row['3rd Layer']) and row['3rd Layer']:
                    tx.run("""
                        MERGE (n2:Nomenclature {name: $n2})
                        MERGE (n3:Nomenclature {name: $n3})
                        MERGE (n2)-[:FEEDS]->(n3)
                        MERGE (sa:ServingArea {name: $serving_area})
                        MERGE (n:Nomenclature {name: $n3})-[:SERVES]->(sa)
                    """, n2=row['2nd Layer'], n3=row['3rd Layer'], serving_area=serving_area)
                else:
                    tx.run("""
                        MERGE (sa:ServingArea {name: $serving_area})
                        MERGE (n:Nomenclature {name: $nomenclature})-[:SERVES]->(sa)
                    """, nomenclature=row['2nd Layer'], serving_area=serving_area)

            elif pd.notna(row['3rd Layer']) and row['3rd Layer']:
                tx.run("""
                    MERGE (n1:Nomenclature {name: $n3})
                    MERGE (n3:Nomenclature {name: $n3})
                    MERGE (n1)-[:FEEDS]->(n3)
                    MERGE (sa:ServingArea {name: $serving_area})
                    MERGE (n:Nomenclature {name: $n3})-[:SERVES]->(sa)
                """, n1=row['1st Layer'], n3=row['3rd Layer'], serving_area=serving_area)
            else:
                tx.run("""
                    MERGE (n1:Nomenclature {name: $n1})
                """, n1=row['1st Layer'])


        # Create SERVES -> Serving Area -> INSIDE -> Location -> IN_ZONE -> Zone relationships
        tx.run("""
            MERGE (sa:ServingArea {name: $serving_area})
            MERGE (l:Location {name: $location})
            MERGE (z:Zone {name: $zone})
            MERGE (n:Nomenclature {name: $nomenclature})-[:SERVES]->(sa)
            MERGE (sa)-[:INSIDE]->(l)
            MERGE (l)-[:IN_ZONE]->(z)
        """, nomenclature=nomenclature, serving_area=serving_area, location=location, zone=zone)

    def load_to_db_dask(self, row)->Optional[str]:
        """
        Loader to Graph DB using Dask
        :param row:
        :return:
        """
        try:
            with self.driver.session(database=settings.NEO4J_DB) as session:
                session.execute_write(self.create_nodes_and_relationships, row)
            return "Success"
        except Exception as e:
            print(f"[LoaderService] Error loading to Neo4j: {e}")
            return None

    def load_to_db(self, all_data_file: str):
        """
        Trigger the loader
        :param all_data_file:
        :return:
        """
        # Create the database if does not exist
        neo4j_service.create_database_if_not_exists(
            db_name=settings.NEO4J_DB
        )
        # Clear the database first
        neo4j_service.clear_database(settings.NEO4J_DB)

        df_all_data = pd.read_csv(all_data_file, sep=",", low_memory=False)
        all_data_rows = df_all_data.to_dict(orient='records')

        # Conventional loop
        with self.driver.session(database=settings.NEO4J_DB) as session:
            for row in all_data_rows:
                session.execute_write(self.create_nodes_and_relationships, row)

        # Load using Dask
        # all_data_bag = db.from_sequence(all_data_rows).persist()
        # all_data_computed = all_data_bag.map(self.load_to_db_dask).compute()
        # successfully_added = [computed for computed in all_data_computed if computed == "Success"]
        neo4j_service.close_connection()
        print("[LoaderService] Data loaded to the Neo4j.")

loader_service = LoaderService()
