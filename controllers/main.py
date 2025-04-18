from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

from constants import (
    ALL_NODES_QUERY,
    ALL_RELATIONS_QUERY,
    DISTINCT_NODE_LABELS_QUERY,
    DISTINCT_RELATION_LABELS_QUERY,
)

class MainPageController:
    def __init__(self):
        """
        Init function
        """

    def fetch_graph(self, tx)->Tuple[
        List[Dict[str, Any]],
        List[Dict[str, Any]]
    ]:
        """
        Function to get all nodes and relations
        :param tx:
        :return:
        """
        # Example Cypher: return all nodes and rels
        resulting_nodes = tx.run(ALL_NODES_QUERY)
        resulting_rels  = tx.run(ALL_RELATIONS_QUERY)
        nodes = [{"data": {"id": item.get("id"), "label": item.get("label", [])[0], "name": item.get("props", {}).get("name", "")}} for item in resulting_nodes.data()]
        rels = [{"data": data} for data in resulting_rels.data()]
        return nodes, rels

    def fetch_unique_node_labels(self, tx)->List[str]:
        """
        Function to query a list of unique node labels
        :param tx:
        :return:
        """
        node_labels = tx.run(DISTINCT_NODE_LABELS_QUERY)
        resulting_labels = [item.get("label", [])[0] for item in node_labels.data()]
        return resulting_labels

    def fetch_unique_relations(self, tx)->List[str]:
        """
        Function to query a list of unique relations labels
        :param tx:
        :return:
        """
        rels_labels = tx.run(DISTINCT_RELATION_LABELS_QUERY)
        resulting_labels = [item.get("label", "") for item in rels_labels.data()]
        return resulting_labels

main_page_controller = MainPageController()
