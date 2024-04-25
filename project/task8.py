import networkx as nx
import pyformlang
from pyformlang.cfg import Epsilon
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex
from pyformlang.rsa import Box
from scipy.sparse import dok_matrix, eye
from project.task2 import graph_to_nfa
from project.task3 import (
    FiniteAutomaton,
    transitive_closure,
    intersect_automata,
    rsm_to_fa,
)


def cfpq_with_tensor(
    rsm: pyformlang.rsa.RecursiveAutomaton,
    graph: nx.MultiDiGraph,
    final_nodes: set[int] = None,
    start_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    rsm_fa = rsm_to_fa(rsm)
    graph_fa = FiniteAutomaton(graph_to_nfa(graph, start_nodes, final_nodes))
    mat_idxs = rsm_fa.revert_mapping()
    graph_idxs = graph_fa.revert_mapping()

    n = len(graph_fa.states_to_states)
    for eps in rsm_fa.eps:
        if eps not in graph_fa.matrix:
            graph_fa.matrix[eps] = dok_matrix((n, n), dtype=bool)
        graph_fa.matrix[eps] += eye(n, dtype=bool)

    len_closure = 0
    while True:
        closure = transitive_closure(intersect_automata(rsm_fa, graph_fa))
        closure = list(zip(*closure.nonzero()))

        if len_closure != len(closure):
            len_closure = len(closure)
        else:
            break

        for i, j in closure:
            frm = mat_idxs[i // n]
            to = mat_idxs[j // n]

            if frm in rsm_fa.start_states and to in rsm_fa.final_states:
                sybl = frm.value[0]
                if sybl not in graph_fa.matrix:
                    graph_fa.matrix[sybl] = dok_matrix((n, n), dtype=bool)
                graph_fa.matrix[sybl][i % n, j % n] = True

    result = set()
    for _, matrix in graph_fa.matrix.items():
        for i, j in zip(*matrix.nonzero()):
            if (
                graph_idxs[i] in rsm_fa.start_states
                and graph_idxs[j] in rsm_fa.final_states
            ):
                result.add((graph_idxs[i], graph_idxs[j]))

    return result


def cfg_to_rsm(cfg: pyformlang.cfg.CFG) -> pyformlang.rsa.RecursiveAutomaton:
    productions = {}
    boxes = set()
    labels = set()
    for production in cfg.productions:
        if len(production.body) == 0:
            regex = Regex(
                " ".join(
                    "$" if isinstance(var, Epsilon) else var.value
                    for var in production.body
                )
            )
        else:
            regex = Regex("$")
        head = Symbol(production.head)
        labels.add(head)
        if head not in productions:
            productions[head] = regex
        else:
            productions[head] = productions[head].union(regex)

    for head, body in productions.items():
        boxes.add(Box(body.to_epsilon_nfa().minimize(), head))

    return pyformlang.rsa.RecursiveAutomaton(labels, Symbol("S"), boxes)


def ebnf_to_rsm(ebnf: str) -> pyformlang.rsa.RecursiveAutomaton:
    return pyformlang.rsa.RecursiveAutomaton.from_text(ebnf)
