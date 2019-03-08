from dijkstar import Graph, find_path


if __name__=='__main__':
    g = Graph()

    g.add_edge('A', 'B', {'cost': 4})
    g.add_edge('B', 'D', {'cost': 2})
    g.add_edge('E', 'D', {'cost': 1})
    g.add_edge('A', 'C', {'cost': 2})
    g.add_edge('C', 'E', {'cost': 5})
    g.add_edge('B', 'C', {'cost': 3})
    g.add_edge('C', 'B', {'cost': 1})

    cost_func = lambda u, v, e, prev_e: e['cost']

    print(find_path(g, 'A', 'B', cost_func=cost_func))
    print(find_path(g, 'A', 'C', cost_func=cost_func))
    print(find_path(g, 'A', 'D', cost_func=cost_func))
    print(find_path(g, 'A', 'E', cost_func=cost_func))




