import pyformlang
from pyformlang.cfg import CFG
from collections import defaultdict, deque
from typing import Deque, Dict, List, Set, Tuple
import networkx


def cfpq_with_hellings(
    cfg: pyformlang.cfg.CFG,
    graph: networkx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> set[Tuple[int, int]]:
    return {
        (start_node, end_node)
        for (start_node, variable, end_node) in work_cfpq_with_hellings(cfg, graph)
        if variable == cfg.start_symbol
        and (start_nodes is None or start_node in start_nodes)
        and (final_nodes is None or end_node in final_nodes)
        and start_node != end_node
    }


def work_cfpq_with_hellings(
    cfg: pyformlang.cfg.CFG, graph: networkx.DiGraph
) -> Set[Tuple[int, pyformlang.cfg.Variable, int]]:
    cfg_in_wnf = cfg_to_weak_normal_form(cfg)

    body_to_head_mapping: Dict[
        Tuple[pyformlang.cfg.Variable, pyformlang.cfg.Variable],
        Set[pyformlang.cfg.Variable],
    ] = defaultdict(set)

    reachability_results: Set[Tuple[int, pyformlang.cfg.Variable, int]] = set()

    start_to_var_finish_mapping: Dict[int, Set[Tuple[pyformlang.cfg.Variable, int]]] = (
        defaultdict(set)
    )
    finish_to_start_var_mapping: Dict[int, Set[Tuple[int, pyformlang.cfg.Variable]]] = (
        defaultdict(set)
    )

    pending_reachabilities: Deque[Tuple[int, pyformlang.cfg.Variable, int]] = deque()

    def add_reachability(start, variable, finish):
        reachability = (start, variable, finish)
        if reachability not in reachability_results:
            reachability_results.add(reachability)
            pending_reachabilities.append(reachability)
            start_to_var_finish_mapping[start].add((variable, finish))
            finish_to_start_var_mapping[finish].add((start, variable))

    edges_by_label: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    for start, finish, attributes in graph.edges.data():
        edges_by_label[attributes["label"]].append((start, finish))

    for production in cfg_in_wnf.productions:
        match production.body:
            case [] | [pyformlang.cfg.Epsilon()]:
                for node in graph.nodes:
                    add_reachability(node, production.head, node)
            case [pyformlang.cfg.Terminal() as terminal]:
                for start, finish in edges_by_label[terminal.value]:
                    add_reachability(start, production.head, finish)
            case [pyformlang.cfg.Variable() as var1, pyformlang.cfg.Variable() as var2]:
                body_to_head_mapping[(var1, var2)].add(production.head)

    while pending_reachabilities:
        (node1, var1, node2) = pending_reachabilities.popleft()
        for start, variable, finish in [
            (node0, variable, node2)
            for (node0, var0) in finish_to_start_var_mapping[node1]
            for variable in body_to_head_mapping[(var0, var1)]
        ] + [
            (node1, variable, node3)
            for (var2, node3) in start_to_var_finish_mapping[node2]
            for variable in body_to_head_mapping[(var1, var2)]
        ]:
            add_reachability(start, variable, finish)
    return reachability_results


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    cfg_simplified = cfg.eliminate_unit_productions().remove_useless_symbols()
    single_terminal_productions = (
        cfg_simplified._get_productions_with_only_single_terminals()
    )
    decomposed_productions = cfg_simplified._decompose_productions(
        single_terminal_productions
    )
    return CFG(
        start_symbol=cfg_simplified.start_symbol, productions=decomposed_productions
    )
