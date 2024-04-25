from pyformlang.cfg import Variable

from typing import Set
import networkx as nx
import pyformlang

from project.task6 import cfg_to_weak_normal_form


def cfpq_with_matrix(
    cfg: pyformlang.cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> set[tuple[int, int]]:
    cfg = cfg_to_weak_normal_form(cfg)
    n = len(graph.nodes)
    materials = {}

    for i, j, data in graph.edges(data=True):
        label = data["label"]

        for product in cfg.productions:
            if (
                len(product.body) == 1
                and isinstance(product.body[0], Variable)
                and product.body[0].value == label
            ):
                if (i, j) not in materials:
                    materials[(i, j)] = set()
                materials[(i, j)].add(product.head)

    while True:
        material_updated = False
        current_meterial = materials.copy()

        for i in range(n):
            for j in range(n):
                for k in range(n):

                    if (i, k) in materials and (k, j) in materials:
                        for product in cfg.productions:

                            if len(product.body) == 2:
                                mat_b, mat_c = product.body
                                if (
                                    mat_b in materials[(i, k)]
                                    and mat_c in materials[(k, j)]
                                ):
                                    if (i, j) not in current_meterial:
                                        current_meterial[(i, j)] = set()
                                    if product.head not in current_meterial[(i, j)]:
                                        current_meterial[(i, j)].add(product.head)
                                        mat_changes = True
        materials = current_meterial
        if not material_updated:
            break

    res = set()

    for i in range(n):
        for j in range(n):

            if (i, j) in materials:
                if (start_nodes is None or i in start_nodes) and (
                    final_nodes is None or j in final_nodes
                ):
                    res.add((i, j))

    return res
