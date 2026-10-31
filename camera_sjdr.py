"""Posicionamento de câmeras de vigilância nas esquinas de São João del-Rei (MG).

Modelagem: cada esquina é um vértice e cada trecho de rua é uma aresta do grafo
viário (extraído do OpenStreetMap). Uma câmera instalada em uma esquina monitora
todos os trechos que chegam nela, então escolher onde instalar o menor número de
câmeras que cubra todas as ruas é o problema da **cobertura mínima de vértices**
(NP-difícil). Este módulo implementa duas heurísticas e um limite inferior para
avaliar a qualidade da solução.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import networkx as nx

ARQUIVO_PADRAO = Path(__file__).resolve().parent / "sjdr.gml"


def carrega_grafo(caminho: str | Path) -> nx.Graph:
    """Lê o GML e devolve um grafo simples com vértices 0..n-1.

    Cada vértice guarda o id do nó no OpenStreetMap (``osm_id``) e cada aresta a
    lista de nomes das ruas daquele trecho (``ruas``).
    """
    original = nx.read_gml(caminho, label="label")
    indice = {rotulo: i for i, rotulo in enumerate(original.nodes)}

    grafo = nx.Graph()
    for rotulo, i in indice.items():
        grafo.add_node(i, osm_id=rotulo)

    for u, v, dados in original.edges(data=True):
        if u == v:
            continue
        nomes = dados.get("name") or []
        nomes = [nomes] if isinstance(nomes, str) else list(nomes)
        a, b = indice[u], indice[v]
        if grafo.has_edge(a, b):
            grafo[a][b]["ruas"] = sorted(set(grafo[a][b]["ruas"]) | set(nomes))
        else:
            grafo.add_edge(a, b, ruas=sorted(set(nomes)))
    return grafo


def eh_cobertura(grafo: nx.Graph, cameras: set[int]) -> bool:
    return all(u in cameras or v in cameras for u, v in grafo.edges)


def cobertura_gulosa(grafo: nx.Graph) -> set[int]:
    """Heurística gulosa com regra das folhas, seguida da remoção de câmeras redundantes.

    A cada passo:
    1. Se alguma esquina tem só uma rua descoberta (uma "folha"), a câmera vai na
       outra ponta dessa rua — existe sempre uma solução ótima que faz essa escolha.
    2. Senão, escolhe a esquina que cobre mais ruas descobertas; no empate, a que
       tem vizinhos com menos ruas descobertas (que seriam mais caros de cobrir depois).

    ``grau[v]`` é o número de ruas ainda descobertas em ``v`` (só para esquinas sem câmera).
    """
    grau = {v: grafo.degree(v) for v in grafo.nodes}
    descobertas = grafo.number_of_edges()
    cameras: set[int] = set()

    while descobertas:
        folha = next((v for v, g in grau.items() if g == 1), None)
        if folha is not None:
            escolhida = next(u for u in grafo[folha] if u in grau)
        else:
            escolhida = max(grau, key=lambda v: (grau[v], -sum(grau.get(u, 0) for u in grafo[v]), -v))

        cameras.add(escolhida)
        for vizinho in grafo[escolhida]:
            if vizinho in grau:
                grau[vizinho] -= 1
                descobertas -= 1
        del grau[escolhida]

    return remove_redundantes(grafo, cameras)


def cobertura_por_emparelhamento(grafo: nx.Graph) -> set[int]:
    """2-aproximação clássica: as duas pontas de cada aresta de um emparelhamento maximal."""
    cameras: set[int] = set()
    for u, v in grafo.edges:
        if u not in cameras and v not in cameras:
            cameras.update((u, v))
    return remove_redundantes(grafo, cameras)


def remove_redundantes(grafo: nx.Graph, cameras: set[int]) -> set[int]:
    """Retira câmeras cujas ruas já estão todas cobertas pelas câmeras vizinhas."""
    cameras = set(cameras)
    for camera in sorted(cameras, key=grafo.degree):
        if all(vizinho in cameras for vizinho in grafo[camera]):
            cameras.remove(camera)
    return cameras


def limite_inferior(grafo: nx.Graph) -> int:
    """Tamanho de um emparelhamento máximo: nenhuma cobertura pode ser menor que isso."""
    return len(nx.max_weight_matching(grafo, maxcardinality=True))


def ruas_monitoradas(grafo: nx.Graph, camera: int) -> list[str]:
    return sorted({rua for vizinho in grafo[camera] for rua in grafo[camera][vizinho]["ruas"]})


METODOS = {"guloso": cobertura_gulosa, "emparelhamento": cobertura_por_emparelhamento}


def main() -> None:
    parser = argparse.ArgumentParser(description="Onde instalar câmeras para monitorar todas as ruas.")
    parser.add_argument("-g", "--grafo", default=ARQUIVO_PADRAO, help="arquivo GML do grafo viário")
    parser.add_argument("-m", "--metodo", choices=METODOS, default="guloso", help="heurística (padrão: guloso)")
    parser.add_argument("-d", "--detalhes", action="store_true", help="lista as ruas monitoradas por cada câmera")
    args = parser.parse_args()

    grafo = carrega_grafo(args.grafo)
    cameras = METODOS[args.metodo](grafo)
    assert eh_cobertura(grafo, cameras)
    minimo = limite_inferior(grafo)

    print(f"Grafo: {grafo.number_of_nodes()} esquinas, {grafo.number_of_edges()} trechos de rua")
    print(f"Método: {args.metodo}")
    print(f"Câmeras necessárias: {len(cameras)} ({len(cameras) / grafo.number_of_nodes():.0%} das esquinas)")
    print(f"Limite inferior: {minimo} -> solução no máximo {len(cameras) / minimo:.2f}x o ótimo")

    if args.detalhes:
        print()
        for camera in sorted(cameras):
            osm_id = grafo.nodes[camera]["osm_id"]
            print(f"Esquina {osm_id} (openstreetmap.org/node/{osm_id}): {', '.join(ruas_monitoradas(grafo, camera))}")


if __name__ == "__main__":
    main()
