# Cypher Queries
ALL_NODES_QUERY = "MATCH (n) RETURN id(n) AS id, labels(n) AS label, n AS props"
ALL_RELATIONS_QUERY = "MATCH (a)-[r]->(b) RETURN id(a) AS source, id(b) AS target, type(r) AS label"
DISTINCT_NODE_LABELS_QUERY = "MATCH (n) RETURN DISTINCT labels(n) AS label"
DISTINCT_RELATION_LABELS_QUERY = "MATCH ()-[r]->() RETURN DISTINCT type(r) AS label"

MAIN_PAGE_GRAPH_LAYOUT = "cose"
