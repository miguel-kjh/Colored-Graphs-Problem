# Colored-Graphs-Problem
 The problem consists in given a graph to choose a combination of colors for all its vertices where the same color does not repeat for any edge, that is, that two connected nodes can not share a color. The solution will be to find the least number of colors that comply with this restriction.

This problem has a trivial solution and is to choose a color for each node, but it will be choosing the worst solution of all in most cases. We start from that we have a number of colors equal to the number of vertices in the graph , that way there will always be a solution available.

Methods to solve it: programming with restrictions (Minizinc), and MIP with Gurobi.
