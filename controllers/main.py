import streamlit as st_inst
from streamlit_agraph import Node, Edge

class MainPageController:
    """
    Controller for the main page
    """

    def fetch_graph_data(self, st: st_inst, driver, cypher_query: str):
        """Fetches graph data from Neo4j using the provided query."""
        nodes = []
        edges = []
        node_ids = set()
        edge_tuples = set()  # To store (source_id, target_id, type) to avoid duplicates

        try:
            with driver.session() as session:
                result = session.run(cypher_query)

                for record in result:
                    path = record["p"]  # The query returns paths assigned to 'p'

                    # Process nodes in the path
                    for node in path.nodes:
                        node_id = node.element_id  # Unique identifier for the node
                        if node_id not in node_ids:
                            node_ids.add(node_id)
                            # --- Node Customization ---
                            # Use 'name' property as label if available, else use the first label or ID
                            label = node.get("name", list(node.labels)[0] if node.labels else str(node.id))
                            title = f"Labels: {', '.join(node.labels)}\nProperties: {dict(node)}"  # Tooltip
                            color = "#ADD8E6"  # Default color (light blue)
                            if "Office" in node.labels:  # Example: color Office nodes differently
                                color = "#FFB6C1"  # Light pink
                            elif "Tenant" in node.labels:
                                color = "#90EE90"  # Light green

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
