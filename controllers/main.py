from typing import List

import streamlit as st_inst
from streamlit_agraph import Node, Edge

from constants import DISTINCT_NODE_LABELS_QUERY, DISTINCT_RELATION_LABELS_QUERY
from settings import settings
from utilities import node_color_palette

class MainPageController:
    """
    Controller for the main page
    """
    def fetch_distinct_nodes(self, driver)->List[str]:
        """Fetches distinct nodes list"""
        with driver.session(database=settings.NEO4J_DB) as session:
            result = session.run(DISTINCT_NODE_LABELS_QUERY)
            result_nodes = [item.get("label", [""])[0] for item in result.data()]
            return result_nodes

    def fetch_distinct_relations(self, driver)->List[str]:
        """Fetches distinct relations list"""
        with driver.session(database=settings.NEO4J_DB) as session:
            result = session.run(DISTINCT_RELATION_LABELS_QUERY)
            result_relations = [item.get("label", [""]) for item in result.data()]
            return result_relations

    def fetch_graph_data(self, st: st_inst, driver, cypher_query: str):
        """Fetches graph data from Neo4j using the provided query."""
        nodes = []
        edges = []
        node_ids = set()
        edge_tuples = set()  # To store (source_id, target_id, type) to avoid duplicates

        try:
            with driver.session(database=settings.NEO4J_DB) as session:
                result = session.run(cypher_query)
                color_palette = node_color_palette()

                for record in result:
                    path = record["p"]  # The query returns paths assigned to 'p'

                    # Process nodes in the path
                    for node in path.nodes:
                        node_id = node.element_id  # Unique identifier for the node
                        if node_id not in node_ids:
                            node_ids.add(node_id)
                            # --- Node Customization ---
                            # Use 'name' property as label if available, else use the first label or ID
                            node_label = list(node.labels)[0] if node.labels else str(node.id)
                            label = node.get("name", node_label)
                            title = f"Labels: {', '.join(node.labels)}\nProperties: {dict(node)}"  # Tooltip
                            color = color_palette.get(node_label, "#000000")

                            nodes.append(
                                Node(
                                    id=node_id,
                                    label=label,
                                    title=title,
                                    color=color
                                )
                            )

                    # Process relationships in the path
                    for rel in path.relationships:
                        start_id = rel.start_node.element_id
                        end_id = rel.end_node.element_id
                        rel_type = rel.type
                        edge_key = (start_id, end_id, rel_type)  # Use tuple including type for uniqueness

                        # Check if this specific edge (including direction and type) has been added
                        if edge_key not in edge_tuples:
                            edge_tuples.add(edge_key)
                            edges.append(Edge(
                                source=start_id,
                                target=end_id,
                                label=rel_type,
                            ))

        except Exception as e:
            st.error(f"Error running Cypher query or processing results: {e}", icon="🚨")
            return [], []  # Return empty lists on error

        if not nodes:
            st.warning("Query returned no results or no paths found.", icon="⚠️")

        return nodes, edges


main_page_controller = MainPageController()
