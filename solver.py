#!/usr/bin/python3.6
import subprocess
import time
from gurobipy import *
import networkx as nx
import re

def output(solution,node_count,method):
    output_data = str(node_count) + ' ' + str(method) + '\n'
    output_data += ' '.join(map(str, solution))
    return output_data


def solution_Minz(edges, edge_count,node_count,end):
    grafo = "grafo = " + str(edges).replace("(", "{").replace(")", "}") + "; "
    enlances = "enlaces = " + str(edge_count) + "; "
    nodos = "numero_nodos = " + str(node_count) + "; "
    coloresNum = node_count
    colores = "colores = " + str(coloresNum) + "; "
    file = open("parametros.dzn", "w")
    parametros = colores + '\n' + enlances + '\n' + grafo + '\n' + nodos
    file.write(parametros)
    file.close()
    st = time.time()
    s = subprocess.check_output(['minizinc', 'color_grafo.mzn', 'parametros.dzn', '--time-limit', str(end)])
    medida_tiempo = time.time() - st
    print("Tiempo " + str(medida_tiempo) + " segundos")
    return re.sub("[b'\-=n]", "", str(s)).replace("\\", "")

def define_graph(edges):
    G = nx.Graph()
    G.add_edges_from(edges)
    return G

def solution_gur(edges,node_count,end,v=4):
    # Create a new model
    G = define_graph(edges)
    m = Model("coloreado de grafos-mapas")
    m.setParam('OutputFlag',False)
    c = node_count
    # Create variables
    colores = [[0 for _ in range(v)] for _ in range(c)]
    for row in range(len(colores)):
        for colum in range(len(colores[row])):
            colores[row][colum] = m.addVar(vtype=GRB.BINARY, name="color " + str(row) + "-" +str(colum))
    obj = m.addVar(vtype=GRB.INTEGER, name="obj")
    m.update()
    m.setParam('TimeLimit',end)
    # Add constraints
    for row in range(len(colores)):
        for colum in range(len(colores[row])):
            m.addConstr(obj >= colum*colores[row][colum])
    for i in range(c):
        m.addConstr(quicksum(colores[i][j] for j in range(v)) == 1)
    for i in range(c):
        m.addConstr(obj>=quicksum(colores[i][j]*j for j in range (v)))
    for clique in list(nx.enumerate_all_cliques(G)):
        if 3 <= len(clique) <= 4:
           m.addConstr(quicksum(colores[i][j]*j for j in range(v) for i in clique) >= sum(range(len(clique)))) 
        if len(clique) > 4:break
    for j in range(v):
        for k in edges:
            m.addConstr(colores[k[0]][j] + colores[k[1]][j] <= 1)

    # Set objective:
    m.setObjective(obj, GRB.MINIMIZE)

    # Optimize model
    m.optimize()
    list_result = []
    for v in m.getVars():
        if v.x > 0:
            pattern = re.compile("\d+")
            list_result.append(pattern.findall(v.varName))
    print("Objective of gurobi %f: " % m.objVal)
    solution = []
    for color in list_result[:len(list_result)-1]:
        solution.append(int(color[1]))
    return solution


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])
    method = "mnz"
    end=60 # 1 min
    if node_count >= 1000:
        method = "gb"
        end = 10800 # 3 horas
    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
    if method == "mnz":
        solution = solution_Minz(edges, edge_count, node_count,end*1000)
        pattern = re.compile("\d+")
        list = []
        for piv in pattern.findall(solution):
            list.append(int(piv))
        return output(list,max(list)+1,0)
    elif method == "gb":
        solution = solution_gur(edges,node_count,end,v=node_count)
        return output(solution,max(solution)+1,1)
    else:
        #Greedy
        solution = range(0,node_count)
        return output(solution, node_count, 2)
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print(
            'This test requires an input file and one method "mnz"(minizinc) or "gb"(gurobi).  Please select one from the data directory. '
            '(i.e. python solver.py ./data/gc_4_1)')

