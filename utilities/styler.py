import random
from typing import List

from st_link_analysis import EdgeStyle, NodeStyle

from constants import EDGE_COLOR_CHOICES, NODE_COLOR_CHOICES

def node_styler(node_list: List[str])->List[NodeStyle]:
    """
    Style from a list of Labels
    :param node_list:
    :return:
    """
    styles = []
    for node in node_list:
        styles.append(NodeStyle(
            node,
            random.choice(NODE_COLOR_CHOICES),
            "name",
        ))
    return styles

def edge_styler(edge_list: List[str])->List[EdgeStyle]:
    """
    Style from a list of Relations
    :param edge_list:
    :return:
    """
    styles = []
    for edge in edge_list:
        styles.append(EdgeStyle(
            edge,
            random.choice(EDGE_COLOR_CHOICES),
            "label",
        ))
    return styles
