import asyncio
import os
import sys

import streamlit as st
from streamlit_agraph import agraph, Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from constants import (
    AVAILABLE_NODES_SELECTION,
    AVAILABLE_QUERY_LIMIT,
    AVAILABLE_RELATIONS_SELECTION,
    CYPHER_TEXTAREA_INSTRUCTION,
    DDL_QUERY_LIMITER_HELPER,
    DEFAULT_MAIN_PAGE_QUERY,
    DEFAULT_SOURCE_NODE_NAME,
    MAIN_INSTRUCTION,
)
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

@st.cache_resource(show_spinner="Fetching Graph Data...")
def populate_dropdown_list():
    """
    Function to populate the Dropdown List
    :return:
    """
    driver = init_neo4j_driver()
    all_unique_nodes = main_page_controller.fetch_distinct_nodes(driver)
    all_unique_relations = main_page_controller.fetch_distinct_relations(driver)
    return all_unique_nodes, all_unique_relations

def run_visualization(
    stlt,
    query: str = DEFAULT_MAIN_PAGE_QUERY
):
    """
    Create Default Visualization
    :return:
    """
    driver = init_neo4j_driver()
    nodes, edges = main_page_controller.fetch_graph_data(
        stlt,
        driver,
        query
    )
    return nodes, edges

def main_page():
    """
    Main Page for the Frontend
    :return:
    """
    st.set_page_config(
        initial_sidebar_state="expanded",
        layout="wide",
        page_title="Building Sensor Graph",
        page_icon=":robot:",
    )
    col_1, col_2, col_3 = st.columns([1, 8, 1])
    with col_2:
        st.title("Building Sensor Management")

    st.session_state.nodes, st.session_state.edges = run_visualization(st)

    with st.sidebar:
        st.session_state.enable_custom_query = st.toggle("Enable Custom Query", value=False)

        if st.session_state.enable_custom_query:
            st.header("Custom Query")
            cypher_query = st.text_area(
                CYPHER_TEXTAREA_INSTRUCTION,
                DEFAULT_MAIN_PAGE_QUERY,
                height=200,
            )
        else:
            st.header("Search from the Graph Database")
            all_nodes, all_relations = populate_dropdown_list()
            nodes_selection = AVAILABLE_NODES_SELECTION if len(all_nodes) < 1 else AVAILABLE_NODES_SELECTION[:-1] + all_nodes + AVAILABLE_NODES_SELECTION[1:]
            source_node = st.selectbox(
                "Select source node",
                options=nodes_selection,
                index=len(nodes_selection) - 1 if len(nodes_selection) > 1 else 0,
            )

            if source_node == "Custom node name...":
                st.session_state.selected_source_node = st.text_input(
                    "Enter the source node name",
                    value=DEFAULT_SOURCE_NODE_NAME
                )
            else:
                st.session_state.selected_source_node = source_node

            relation_selection = AVAILABLE_RELATIONS_SELECTION if len(all_relations) < 1 else AVAILABLE_RELATIONS_SELECTION + all_relations
            st.session_state.selected_relation = st.selectbox("Select relation", options=relation_selection)

            destination_node = st.selectbox(
                "Select destination node",
                options=nodes_selection,
                index=len(nodes_selection) - 1 if len(nodes_selection) > 1 else 0,
            )

            if destination_node == "Custom node name...":
                st.session_state.selected_destination_node = st.text_input(
                    "Enter the destination node name"
                )
            else:
                st.session_state.selected_destination_node = destination_node

            st.session_state.limit_query = st.selectbox(
                "Select the query limiter",
                options=AVAILABLE_QUERY_LIMIT,
                index=2,
                help=DDL_QUERY_LIMITER_HELPER,
            )

        run_query_button = st.button(":mag_right: Run Query")
        if run_query_button:
            st.session_state.nodes, st.session_state.edges = run_visualization(st, query=cypher_query)

    if st.session_state.nodes:
        with col_2:
            st.subheader("Graph Visualization")
            st.code(
                "Created by: Jalaluddin Al Mursyidy Fadhlurrahman",
                language=None
            )
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
        agraph(nodes=st.session_state.nodes, edges=st.session_state.edges, config=agraph_config)
    else:
        pass

if __name__ == "__main__":
    main_page()
