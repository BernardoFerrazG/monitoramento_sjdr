import networkx as nx
from collections import defaultdict

def cobertura_de_vertices(graph):
    arestas_nao_cobertas = set(graph.edges())
    cameras = []
    
    while arestas_nao_cobertas:
        grau_vertice = defaultdict(int)
        for i, j in arestas_nao_cobertas:
            grau_vertice[i] += 1
            grau_vertice[j] += 1
        
        vertice = max(grau_vertice, key=grau_vertice.get)
        
        cameras.append(vertice)
        
        for i in list(graph[vertice]):
            arestas_nao_cobertas.discard((min(vertice, i), max(vertice, i)))
    
    return cameras


def cobertura_de_arestas(cameras, graph):
    cobertura = {}
    for camera in cameras:
        ruas_monitoradas = []
        for vizinho in graph[camera]:
            edge_data = graph.get_edge_data(camera, vizinho)
            if edge_data:
                ruas_monitoradas.append(edge_data.get('name'))
        cobertura[camera] = ruas_monitoradas
    return cobertura


def obtem_grafo(caminho_arquivo):

    graph = nx.read_gml(caminho_arquivo, label='label')

    label_id = {label: index for index, label in enumerate(graph.nodes)}
    
    grafo_aux = nx.Graph()
    for node in graph.nodes:
        grafo_aux.add_node(label_id[node], label=node)
    
    for i, j, data in graph.edges(data=True):
        grafo_aux.add_edge(label_id[i], label_id[j], name=data.get('name'))
    
    return grafo_aux

caminho_arquivo = 'sjdr.gml' 
graph = obtem_grafo(caminho_arquivo)

cameras = cobertura_de_vertices(graph)

cobertura = cobertura_de_arestas(cameras, graph)

print("Câmeras instaladas nas esquinas:", cameras)
for camera in cameras:
    print(f"Câmera na esquina {camera} monitorando as ruas: {cobertura[camera]}")
