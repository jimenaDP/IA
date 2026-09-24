"""SAT solver basado en el algoritmo DPLL (Davis-Putnam-Logemann-Loveland).

Referencia: pseudocódigo ¿SATISFACIBLE-DPLL?(s) / DPLL(clausulas, simbolos, modelo)
"Artificial Intelligence. A modern approach" (2nd edition, fig. 7.16), visto en la
clase de teoría del 18/09.

Representación:
    - Un literal es un entero distinto de cero. Un símbolo P se representa con el
      entero positivo devuelto por id_var(); su negación ¬P se representa como
      el mismo entero en negativo.
    - Una cláusula es una lista de literales (disyunción).
    - Una sentencia en FNC (forma normal conjuntiva) es una lista de cláusulas
      (conjunción de disyunciones) -- exactamente lo que genera generate_rules().
    - Un modelo es un dict {simbolo: True/False}.
"""


def clause_status(clause, model):
    """Devuelve True si la clausula esta satisfecha, False si esta falsificada,
    o None si todavia no se puede determinar con el modelo (parcial) actual."""
    undetermined = False
    for lit in clause:
        sym = abs(lit)
        if sym not in model:
            undetermined = True
        elif (lit > 0) == model[sym]:
            return True  # un literal verdadero basta para satisfacer la clausula
    return None if undetermined else False


def find_pure_symbol(symbols, clauses, model):
    """Heuristica de simbolo puro: un simbolo es puro si aparece siempre con el
    mismo signo en todas las clausulas todavia no satisfechas."""
    sign = {}
    for clause in clauses:
        if clause_status(clause, model) is True:
            continue  # esta clausula ya no aporta informacion
        for lit in clause:
            sym = abs(lit)
            if sym in model:
                continue
            polarity = lit > 0
            if sym not in sign:
                sign[sym] = polarity
            elif sign[sym] != polarity:
                sign[sym] = None  # aparece en ambas polaridades: no es puro

    for sym in symbols:
        if sym not in model and sign.get(sym) is not None:
            return sym, sign[sym]
    return None, None


def find_unit_clause(clauses, model):
    """Heuristica de clausula unitaria: una clausula con un unico literal sin
    asignar obliga a fijar ese literal a verdadero."""
    for clause in clauses:
        unassigned = None
        satisfied = False
        count = 0
        for lit in clause:
            sym = abs(lit)
            if sym in model:
                if (lit > 0) == model[sym]:
                    satisfied = True
                    break
            else:
                count += 1
                unassigned = lit
        if satisfied or count != 1:
            continue
        return abs(unassigned), unassigned > 0
    return None, None


def dpll(clauses, symbols, model):
    """Devuelve (True, modelo) si el modelo (parcial) se puede extender a un
    modelo que satisface todas las clausulas; (False, None) en caso contrario."""
    all_satisfied = True
    for clause in clauses:
        status = clause_status(clause, model)
        if status is False:
            return False, None
        if status is not True:
            all_satisfied = False
    if all_satisfied:
        return True, model

    remaining = [s for s in symbols if s not in model]
    if not remaining:
        return False, None

    # Terminacion anticipada + heuristicas, en el mismo orden que el pseudocodigo
    sym, val = find_pure_symbol(remaining, clauses, model)
    if sym is not None:
        return dpll(clauses, symbols, {**model, sym: val})

    sym, val = find_unit_clause(clauses, model)
    if sym is not None:
        return dpll(clauses, symbols, {**model, sym: val})

    # Ramificacion sobre el primer simbolo sin asignar
    p = remaining[0]
    sat, result = dpll(clauses, symbols, {**model, p: True})
    if sat:
        return True, result
    return dpll(clauses, symbols, {**model, p: False})


def satisfacible(clausulas, simbolos=None):
    """¿SATISFACIBLE-DPLL?(s): comprueba si una sentencia en FNC (lista de
    clausulas) es satisfacible. Devuelve (bool, modelo_o_None)."""
    if simbolos is None:
        simbolos = set()
        for clause in clausulas:
            for lit in clause:
                simbolos.add(abs(lit))
        simbolos = list(simbolos)
    return dpll(clausulas, simbolos, {})


if __name__ == "__main__":
    # Prueba rápida: B <=> (P1 v P2), con FNC ya calculada en GeneracionNormas.py
    # (-B v P1 v P2) ∧ (-P1 v B) ∧ (-P2 v B)
    B, P1, P2 = 1, 2, 3
    fnc = [[-B, P1, P2], [-P1, B], [-P2, B]]

    # Si sabemos que B es falso, ninguno de P1, P2 puede ser verdadero
    sat, modelo = satisfacible(fnc + [[B]])
    print("BC con B=verdadero -> satisfacible:", sat, modelo)

    sat, modelo = satisfacible(fnc + [[-B], [P1]])
    print("BC con B=falso, P1=verdadero -> satisfacible (debe ser False):", sat, modelo)
