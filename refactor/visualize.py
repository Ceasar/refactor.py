import matplotlib.pyplot as plt
import networkx as nx


def draw(deps):
    """Draw a dependency graph *deps*."""
    graph = nx.DiGraph()
    for node in deps:
        graph.add_node(node)
    for node, neighbors in deps.items():
        for neighbor in neighbors:
            graph.add_edge(node, neighbor)
    pos = nx.spring_layout(graph, iterations=100)
    nx.draw(graph, pos)
    nx.draw_networkx_labels(graph, pos)
    plt.show()
