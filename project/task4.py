from project.task3 import FiniteAutomaton, intersect_automata, transitive_closure


def reachability_with_constraints(
    fa: FiniteAutomaton, constraints_fa: FiniteAutomaton
) -> dict[int, set[int]]:
    inter = intersect_automata(fa, constraints_fa, lbl=False)
    closure = transitive_closure(inter)

    map = {v: i for i, v in fa.states_to_states.items()}
    con = len(constraints_fa.states_to_states)
    r = dict()

    for start in fa.start_states:
        r[start] = set()

    for v, u in zip(*closure.nonzero()):
        if v in inter.start_states and u in inter.final_states:
            r[map[v // con]].add(map[u // con])

    return r
