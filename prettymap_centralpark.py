import prettymaps
from matplotlib import pyplot as plt

plot = prettymaps.plot(
    # Central Park, New York City coordinates
    '40.785091, -73.968285',
    circle = True,  # Central Park is rectangular, not circular
    radius = 2800,
    layers = {
        "green": {
            "tags": {
                "landuse": ["grass", "meadow"],
                "natural": ["island", "wood", "scrub"],
                "leisure": "park"
            }
        },
        "forest": {
            "tags": {
                "landuse": "forest",
                "natural": "tree_row"
            }
        },
        "water": {
            "tags": {
                "natural": ["water", "bay"],
                "water": ["pond", "lake", "reservoir"]
            }
        },
        "parking": {
            "tags": {
                "amenity": "parking",
                "highway": "pedestrian",
                "man_made": "pier"
            }
        },
        "streets": {
            "width": {
                "motorway": 5,
                "trunk": 5,
                "primary": 4.5,
                "secondary": 4,
                "tertiary": 3.5,
                "residential": 3,
                "footway": 1,
                "path": 1,
            }
        },
        "building": {
            "tags": {"building": True},
        },
    },
    style = {
        "background": {
            "fc": "#F2F4CB",
            "ec": "#dadbc1",
            "hatch": "ooo...",
        },
        "perimeter": {
            "fc": "#F2F4CB",
            "ec": "#dadbc1",
            "lw": 0,
            "hatch": "ooo...",
        },
        "green": {
            "fc": "#D0F1BF",
            "ec": "#2F3737",
            "lw": 1,
        },
        "forest": {
            "fc": "#64B96A",
            "ec": "#2F3737",
            "lw": 1,
        },
        "water": {
            "fc": "#a1e3ff",
            "ec": "#2F3737",
            "hatch": "ooo...",
            "hatch_c": "#85c9e6",
            "lw": 1,
        },
        "parking": {
            "fc": "#F2F4CB",
            "ec": "#2F3737",
            "lw": 1,
        },
        "streets": {
            "fc": "#2F3737",
            "ec": "#475657",
            "alpha": 1,
            "lw": 0,
        },
        "building": {
            "palette": [
                "#FFC857",
                "#E9724C",
                "#C5283D"
            ],
            "ec": "#2F3737",
            "lw": 0.5,
        }
    }
)

plt.savefig('central_park_nyc.jpg', dpi=300, bbox_inches='tight')
plt.show()