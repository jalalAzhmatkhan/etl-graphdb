import asyncio
import os
import sys

import streamlit as st
from streamlit_agraph import agraph, Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from constants import DEFAULT_MAIN_PAGE_QUERY, MAIN_INSTRUCTION
from controllers import main_page_controller
from services import neo4j_service

@st.cache_resource(show_spinner="Connecting to Neo4j DB...")
def init_neo4j_driver():
    """
    Function to initialize Neo4j Driver
    :return:
    """
    try:
        neo4j_service.neo4j_driver.verify_connectivity()
        return neo4j_service.neo4j_driver
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {e}", icon="🚨")
        return None

def default_visualization(stlt):
    """
    Create Default Visualization
    :return:
    """
    driver = init_neo4j_driver()
    nodes, edges = main_page_controller.fetch_graph_data(
        stlt,
        driver,
        DEFAULT_MAIN_PAGE_QUERY
    )
    return nodes, edges

def main_page():
    """
    Main Page for the Frontend
    :return:
    """
    st.set_page_config(
        initial_sidebar_state="collapsed",
        layout="wide",
        page_title="Building Sensor Graph",
        page_icon=":robot:",
    )
    col_1, col_2, col_3 = st.columns([1, 8, 1])
    with col_2:
        st.title("Building Sensor")

    nodes, edges = default_visualization(st)
    if nodes:
        with col_2:
            st.subheader("Graph Visualization")
            st.write(MAIN_INSTRUCTION)

        agraph_config = Config(
            directed=True,
            height=500,
            highlistNearest=True,
            nodeHighlightBehavior=True,
            physics=True,
            solver="forceAtlas2Based",
            stabilization=True,
            width="100%",
        )
        agraph(nodes=nodes, edges=edges, config=agraph_config)
    else:
        pass

if __name__ == "__main__":
    main_page()
