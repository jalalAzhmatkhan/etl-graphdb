import random
from typing import Dict

from constants import (
    BLUE_NODE_COLOR_CHOICES,
    ORANGE_NODE_COLOR_CHOICES,
    PINK_NODE_COLOR_CHOICES,
    RED_NODE_COLOR_CHOICES,
)

def node_color_palette()->Dict[str, str]:
    """
    Color chooser for each unique node entity
    :return:
    """
    nomenclature_color = random.choice(ORANGE_NODE_COLOR_CHOICES)
    sensor_object_color = random.choice(PINK_NODE_COLOR_CHOICES)
    location_color = random.choice(BLUE_NODE_COLOR_CHOICES)
    serving_area_color = random.choice(RED_NODE_COLOR_CHOICES)
    zone_color = random.choice(RED_NODE_COLOR_CHOICES)

    return {
        "Nomenclature": nomenclature_color,
        "SensorObject": sensor_object_color,
        "Location": location_color,
        "ServingArea": serving_area_color,
        "Zone": zone_color,
    }
