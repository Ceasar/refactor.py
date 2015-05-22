import math
import random

import matplotlib.pyplot as plt
import networkx as nx


def exploded_layout(nodes, edges, iterations=100, damp=0.9):
    """
    Create a layout that shows the relationship of the nodes in the graph.

    :param nodes:
        A list of nodes.
    :param edges:
        A list of *(from, to)* tuples representing the edges.
    :param iterations:
        The number of times to calculate the positions of nodes. Higher numbers
        make the graph more stable, but take longer to compute.
    :param damp:
        A float between 0.0 and 1.0 that reduces the velocity of nodes in the
        simulation, causing the layout to converge.
    :return:
        Mapping from nodes to tuples representing X-Y coordinates.

    >>> g = nx.path_graph(4)
    >>> g.nodes()
    [0, 1, 2, 3]
    >>> exploded_layout(g)
    {
        0: (27.4453656337274, 35.47624605641406),
        1: (22.440841959945352, 33.99462287034427),
        2: (17.077906616739952, 32.55854888384641),
        3: (12.039180712292593, 31.169449425573674)
    }
    """
    n = len(nodes)
    positions = {
        node: (random.random() * n, random.random() * n)
        for node in nodes
    }
    velocity = {
        node: (random.random() * n, random.random() * n)
        for node in nodes
    }
    for _ in xrange(iterations):
        # Push nodes on edges away from each other
        for n1, n2 in edges:
            x1, y1 = positions[n1]
            x2, y2 = positions[n2]
            x, y = x1 - x2, y1 - y2
            distance = math.sqrt(x * x + y * y)
            dx1, dy1 = velocity[n1]
            velocity[n1] = (
                dx1 + (math.cos(math.atan2(y, x)) * (n - distance) / n),
                dy1 + (math.sin(math.atan2(y, x)) * (n - distance) / n),
            )
            dx2, dy2 = velocity[n2]
            velocity[n2] = (
                dx2 + (math.cos(math.atan2(-y, -x)) * (n - distance) / n),
                dy2 + (math.sin(math.atan2(-y, -x)) * (n - distance) / n),
            )

        # Push all nodes away from other nodes to avoid criss-crossing
        items = positions.items()
        for i, (n1, (x1, y1)) in enumerate(items):
            for n2, (x2, y2) in items[i + 1:]:
                x, y = x1 - x2, y1 - y2
                # force decreases with distance
                f = 1.0 / (math.sqrt(x * x + y * y) + 1)
                dx1, dy1 = velocity[n1]
                velocity[n1] = (
                    dx1 + (math.cos(math.atan2(y, x)) * f),
                    dy1 + (math.sin(math.atan2(y, x)) * f),
                )
                dx2, dy2 = velocity[n2]
                velocity[n2] = (
                    dx2 + (math.cos(math.atan2(-y, -x)) * f),
                    dy2 + (math.sin(math.atan2(-y, -x)) * f),
                )

        # Set node positions
        for node, (x, y) in positions.items():
            dx, dy = velocity[node]
            positions[node] = x + dx, y + dy
            velocity[node] = dx * damp, dy * damp

    return positions


def draw(deps):
    """Draw a dependency graph for *deps*."""
    graph = nx.DiGraph()
    for node in deps:
        graph.add_node(node)
    for node, neighbors in deps.items():
        for neighbor in neighbors:
            graph.add_edge(node, neighbor)
    pos = exploded_layout(graph.nodes(), graph.edges())
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=[
            'r' if deps.get(node) else 'b'
            for node in graph.nodes()
        ],
        alpha=0.8,
        edge_color='w',
    )
    nx.draw_networkx_edges(graph, pos, alpha=0.5)
    nx.draw_networkx_labels(graph, pos)
    plt.show()
