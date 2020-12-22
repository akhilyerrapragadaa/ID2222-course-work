import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.cluster import KMeans

k = 4
filename = "example2.dat"

# Read the data
graph_unsorted = nx.read_edgelist(filename, delimiter=",", nodetype=int, data=(("weight", int), ))
graph = nx.Graph()
graph.add_nodes_from(sorted(graph_unsorted.nodes.keys()))
graph.add_edges_from(graph_unsorted.edges)

nx.draw(graph, node_size=10)

# 1. Form the affinity matrix
A = np.zeros([graph.number_of_nodes(), graph.number_of_nodes()])
for edge in graph.edges:
    A[edge[0] - 1, edge[1] - 1] = 1
    A[edge[1] - 1, edge[0] - 1] = 1

# 2. Define D and L
D = np.diag(np.sum(A, axis=1))
D_inv = np.linalg.inv(np.sqrt(D))
L = np.dot(np.dot(D_inv, A), D_inv)

# 3. Find eigenvectors
_, eigenvectors = np.linalg.eigh(L)  # Gives eigenvectors in acceding order
X = eigenvectors[:, -k:]             # Take k largest eigenvectors

# 4. Form matrix Y by renormalizing X
Y = np.zeros_like(X)
for i in range(k):
    square = X[:, i].dot(X[:, i])
    Y[:, i] = X[:, i] / np.sqrt(square)

# 5. Apply k-means cluster
labels = KMeans(n_clusters=k).fit(Y).labels_

plt.figure()
nx.draw(graph, node_size=10, node_color=labels)
plt.show()
