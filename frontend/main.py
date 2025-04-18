import asyncio
import os
import sys

import streamlit as st
from st_link_analysis import st_link_analysis

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from constants import MAIN_PAGE_GRAPH_LAYOUT
from controllers import main_page_controller
from services import neo4j_service
from settings import settings
from utilities import edge_styler, node_styler

@st.cache_resource
def init_neo4j_driver():
    """
    Function to initialize Neo4j Driver
    :return:
    """
    return neo4j_service.neo4j_driver

@st.cache_data
def get_all_nodes_and_relations(_driver):
    """
    Interface function to get All nodes and relations
    :return:
    """
    with _driver.session(database=settings.NEO4J_DB) as session:
        nodes, rels = session.read_transaction(main_page_controller.fetch_graph)
        distinct_node_lbl = session.read_transaction(main_page_controller.fetch_unique_node_labels)
        distinct_rel_lbl = session.read_transaction(main_page_controller.fetch_unique_relations)
        return nodes, rels, node_styler(distinct_node_lbl), edge_styler(distinct_rel_lbl)

def main_page():
    """
    Main Page for the Frontend
    :return:
    """
    st.set_page_config(
        page_title="Building Sensors Graph",
    )

    neo4j_driver = init_neo4j_driver()
    nodes, rels, node_styles, edge_styles = get_all_nodes_and_relations(neo4j_driver)

    graph_elements = {
        "nodes": nodes,
        "edges": rels
    }

    col_1, col_2, col_3 = st.columns([1, 7, 1])
    with col_2:
        st.title("Building Sensors Graph")
        st.write("A simple visualization graph of sensors and their connections in a building.")

        st_link_analysis(
            graph_elements,
            MAIN_PAGE_GRAPH_LAYOUT,
            node_styles,
            edge_styles
        )

if __name__ == "__main__":
    main_page()
