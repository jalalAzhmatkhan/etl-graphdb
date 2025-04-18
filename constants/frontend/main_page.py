AVAILABLE_RELATION_DIRECTION = ["Undirected", "Directed-Incoming", "Directed-Outgoing"]
AVAILABLE_NODES_SELECTION = [
    "*",
    "Custom node name..."
]
AVAILABLE_RELATIONS_SELECTION = [
    "*",
]
AVAILABLE_QUERY_LIMIT = [
    "10",
    "25",
    "50",
    "100",
    "150",
    "200",
    "No limit :warning:"
]
CYPHER_TEXTAREA_INSTRUCTION = """
Enter Cypher Query (must return paths 'p')
"""
DDL_QUERY_LIMITER_HELPER = "Querying too many data may affect the time taken to load it..."
DEFAULT_SOURCE_NODE_NAME = "L4 Tenant Office"
MAIN_INSTRUCTION = """
    Hover on a node to see the details.\n
    You can zoom in and out by using Ctrl + Mouse Wheel or just the Mouse Wheel.
    Drag the area below to drag the graph.
"""
