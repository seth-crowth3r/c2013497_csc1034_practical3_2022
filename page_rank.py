import sys
import os
import time
import argparse
from progress import Progress
import random


def load_graph(args):
    """Load graph from text file

    Parameters:
    args -- arguments named tuple

    Returns:
    A dict mapping a URL (str) to a list of target URLs (str).
    """
    nodes = dict()
    # Iterate through the file line by line
    for line in args.datafile:
        # And split each line into two URLs
        node, target = line.split()

        if node not in nodes:
            nodes[node] = []
        nodes[node].append(target)

    return nodes


def print_stats(graph):
    """Print number of nodes and edges in the given graph"""
    print(f"Number of nodes: {len(graph)}")

    edge_count = 0
    for node_list in graph.values():
        edge_count += len(node_list) # Counts number of adjacent nodes for each node and sums them to get edge count

    print(f"Number of edges: {edge_count}")


def stochastic_page_rank(graph, args):
    """Stochastic PageRank estimation

    Parameters:
    graph -- a graph object as returned by load_graph()
    args -- arguments named tuple

    Returns:
    A dict that assigns each page its hit frequency

    This function estimates the Page Rank by counting how frequently
    a random walk that starts on a random node will after n_steps end
    on each node of the given graph.
    """
    from random import choice

    # Initialize hit count of all nodes to 0
    hit_count = dict()
    for node in graph:
        hit_count[node] = 0

    # Stochastic page rank algorithm
    for x in range(args.repeats):
        current_node = choice(list(graph.keys())) # Choose a random starting node
        for y in range(args.steps):
            current_node = choice(graph[current_node]) # Choose a random adjacent node to the current node
        hit_count[current_node] += 1 / args.repeats

    return hit_count


def distribution_page_rank(graph, args):
    """Probabilistic PageRank estimation

    Parameters:
    graph -- a graph object as returned by load_graph()
    args -- arguments named tuple

    Returns:
    A dict that assigns each page its probability to be reached

    This function estimates the Page Rank by iteratively calculating
    the probability that a random walker is currently on any node.
    """
    # Initialize probability of reaching a node to 1 / num nodes
    node_prob = dict()
    num_nodes = len(graph)
    for node in graph:
        node_prob[node] = 1 / num_nodes

    for x in range(args.steps):
        next_prob = dict()

        # Initialize next_prob dictionary
        for node in graph:
            next_prob[node] = 0

        for node in graph:
            p = node_prob[node] / len(graph[node])
            for adj_node in graph[node]:
                next_prob[adj_node] += p

        node_prob = next_prob

    return node_prob


parser = argparse.ArgumentParser(description="Estimates page ranks from link information")
parser.add_argument('datafile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                    help="Textfile of links among web pages as URL tuples")
parser.add_argument('-m', '--method', choices=('stochastic', 'distribution'), default='stochastic',
                    help="selected page rank algorithm")
parser.add_argument('-r', '--repeats', type=int, default=1_000_000, help="number of repetitions")
parser.add_argument('-s', '--steps', type=int, default=100, help="number of steps a walker takes")
parser.add_argument('-n', '--number', type=int, default=20, help="number of results shown")


if __name__ == '__main__':
    args = parser.parse_args()
    algorithm = distribution_page_rank if args.method == 'distribution' else stochastic_page_rank

    graph = load_graph(args)

    print_stats(graph)

    start = time.time()
    ranking = algorithm(graph, args)
    stop = time.time()
    time = stop - start

    top = sorted(ranking.items(), key=lambda item: item[1], reverse=True)
    sys.stderr.write(f"Top {args.number} pages:\n")
    print('\n'.join(f'{100*v:.2f}\t{k}' for k,v in top[:args.number]))
    sys.stderr.write(f"Calculation took {time:.2f} seconds.\n")
