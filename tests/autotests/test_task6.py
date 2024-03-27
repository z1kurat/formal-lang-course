from project import convert_to_weak_cnf, read_grammar_from_file
from pyformlang.cfg import CFG


def test_conversion_to_weak_cnf():
    """
    [
        V -> Terminal(sees),
        Det -> Terminal(the),
        Y6 -> VP PUNC,
        PUNC -> Terminal(!),
        Det -> Terminal(a),
        N -> Terminal(gorilla),
        NP -> Det N,
        PUNC -> Terminal(.),
        NP -> Terminal(georges),
        Det -> Terminal(an),
        V -> Terminal(buys),
        N -> Terminal(dog),
        NP -> Terminal(jacques),
        S -> NP Y6,
        VP -> V NP,
        N -> Terminal(carrots),
        V -> Terminal(touches),
        NP -> Terminal(leo)
    ]
    """
    cfg: CFG = read_grammar_from_file("./tests/cfg.txt")
    weak_cnf_cfg = convert_to_weak_cnf(cfg)

    assert len(weak_cnf_cfg.productions) == 18
