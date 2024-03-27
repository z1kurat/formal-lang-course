from pyformlang.cfg import CFG
from pyformlang.cfg import CFG, Variable, Terminal, Production


def read_grammar_from_file(file_path):
    with open(file_path, "r") as file:
        cfg_text = file.read()
    cfg = CFG.from_text(cfg_text)
    return cfg


def eliminate_epsilon_rules(cfg: CFG) -> CFG:
    nullable_variables = {
        var
        for var in cfg.variables
        if any(len(prod.body) == 0 for prod in cfg.productions if prod.head == var)
    }
    changed = True
    while changed:
        changed = False
        for production in cfg.productions:
            if (
                all(symbol in nullable_variables for symbol in production.body)
                and production.head not in nullable_variables
            ):
                nullable_variables.add(production.head)
                changed = True

    new_productions = set()
    for production in cfg.productions:
        if len(production.body) != 0:
            new_productions.add(production)
            for i, symbol in enumerate(production.body):
                if symbol in nullable_variables:
                    new_body = list(production.body)
                    del new_body[i]
                    if new_body:
                        new_productions.add(Production(production.head, new_body))
                    else:
                        if production.head != cfg.start_symbol:
                            new_productions.add(Production(production.head, []))
    return CFG(
        variables=cfg.variables,
        terminals=cfg.terminals,
        start_symbol=cfg.start_symbol,
        productions=list(new_productions),
    )


def eliminate_long_rules(cfg: CFG) -> CFG:
    new_productions = []
    for production in cfg.productions:
        head = production.head
        body = production.body
        if len(body) <= 2:
            new_productions.append(production)
            continue
        while len(body) > 2:
            new_var = Variable(f"Y{len(new_productions)}")
            new_productions.append(Production(head, [body[0], new_var]))
            head = new_var
            body = body[1:]
        new_productions.append(Production(head, body))

    return CFG(
        variables=cfg.variables,
        terminals=cfg.terminals,
        start_symbol=cfg.start_symbol,
        productions=new_productions,
    )


def eliminate_chain_rules(cfg: CFG) -> CFG:
    chain_rules = [
        (prod.head, prod.body[0])
        for prod in cfg.productions
        if len(prod.body) == 1 and isinstance(prod.body[0], Variable)
    ]
    direct_chains = {var: {var} for var in cfg.variables}
    for head, body in chain_rules:
        direct_chains[head].add(body)

    for var in cfg.variables:
        for head in list(direct_chains):
            if var in direct_chains[head]:
                direct_chains[head] = direct_chains[head].union(direct_chains[var])

    new_productions = [
        prod
        for prod in cfg.productions
        if not (len(prod.body) == 1 and isinstance(prod.body[0], Variable))
    ]
    for head, bodies in direct_chains.items():
        for body in bodies:
            for prod in cfg.productions:
                if prod.head == body and prod not in new_productions:
                    new_productions.append(Production(head, prod.body))
    return CFG(
        variables=cfg.variables,
        terminals=cfg.terminals,
        start_symbol=cfg.start_symbol,
        productions=new_productions,
    )


def eliminate_useless_symbols(cfg: CFG) -> CFG:
    reachable = {cfg.start_symbol}
    changes = True
    while changes:
        changes = False
        for production in cfg.productions:
            if production.head in reachable:
                for symbol in production.body:
                    if symbol not in reachable:
                        reachable.add(symbol)
                        changes = True

    all_symbols = set(cfg.variables).union(cfg.terminals)
    productive = {sym for sym in all_symbols if isinstance(sym, Terminal)}
    changes = True
    while changes:
        changes = False
        for production in cfg.productions:
            if (
                all(
                    symbol in productive or symbol in reachable
                    for symbol in production.body
                )
                and production.head not in productive
            ):
                productive.add(production.head)
                changes = True

    useful_symbols = reachable.intersection(productive)
    new_productions = [
        prod
        for prod in cfg.productions
        if prod.head in useful_symbols
        and all(sym in useful_symbols for sym in prod.body)
    ]

    new_variables = {var for var in cfg.variables if var in useful_symbols}
    new_terminals = {term for term in cfg.terminals if term in useful_symbols}

    return CFG(
        variables=new_variables,
        terminals=new_terminals,
        start_symbol=cfg.start_symbol,
        productions=new_productions,
    )


def convert_to_weak_cnf(cfg: CFG) -> CFG:
    cfg = eliminate_long_rules(cfg)
    cfg = eliminate_epsilon_rules(cfg)
    cfg = eliminate_chain_rules(cfg)
    cfg = eliminate_useless_symbols(cfg)
    return cfg
