import itertools

import networkx as nx
import pytest

from camera_sjdr import (
    ARQUIVO_PADRAO,
    carrega_grafo,
    cobertura_gulosa,
    cobertura_por_emparelhamento,
    eh_cobertura,
    limite_inferior,
    remove_redundantes,
    ruas_monitoradas,
)


@pytest.fixture(scope="module")
def sjdr():
    return carrega_grafo(ARQUIVO_PADRAO)


def cobertura_otima(grafo):
    for k in range(grafo.number_of_nodes() + 1):
        for candidatos in itertools.combinations(grafo.nodes, k):
            if eh_cobertura(grafo, set(candidatos)):
                return k


@pytest.mark.parametrize("metodo", [cobertura_gulosa, cobertura_por_emparelhamento])
def test_cobre_todas_as_ruas_de_sjdr(sjdr, metodo):
    cameras = metodo(sjdr)
    assert eh_cobertura(sjdr, cameras)
    assert len(cameras) >= limite_inferior(sjdr)


@pytest.mark.parametrize("metodo", [cobertura_gulosa, cobertura_por_emparelhamento])
@pytest.mark.parametrize("seed", range(10))
def test_grafos_pequenos_contra_otimo(metodo, seed):
    grafo = nx.gnp_random_graph(10, 0.3, seed=seed)
    cameras = metodo(grafo)
    assert eh_cobertura(grafo, cameras)
    assert len(cameras) <= 2 * cobertura_otima(grafo)


def test_remove_redundantes_mantem_cobertura():
    estrela = nx.star_graph(5)  # centro 0 ligado a 1..5
    cameras = remove_redundantes(estrela, set(estrela.nodes))
    assert eh_cobertura(estrela, cameras)
    assert len(cameras) < 6


def test_nomes_de_ruas_sao_unicos_e_planos(sjdr):
    for camera in cobertura_gulosa(sjdr):
        ruas = ruas_monitoradas(sjdr, camera)
        assert ruas == sorted(set(ruas))
        assert all(isinstance(rua, str) for rua in ruas)
