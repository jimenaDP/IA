"""Agente basado en conocimiento para el mundo de Wumpus (fig. 7.1 / 7.19).

Implementa las dos tareas de un agente basado en conocimiento:
    - DECIR: anadir sentencias nuevas a la BC (lo que el agente percibe)
    - PREGUNTAR: consultar que se sabe en la BC (si una casilla es segura)

La inferencia se hace por refutacion, apoyandose en el teorema:
    BC |= alpha   <=>   (BC ∧ ¬alpha) es insatisfacible

que es exactamente para lo que sirve el SAT solver (satisfacible() en
sat_solver.py): si al anadir la negacion de lo que queremos probar la base
se vuelve insatisfacible, es que la BC ya implicaba esa sentencia.
"""

from sat_solver import satisfacible
from GeneracionNormas import generate_rules, id_var, get_neighbors


class BaseConocimiento:
    def __init__(self, N):
        self.N = N
        self.clausulas = generate_rules(N)
        # Hecho inicial: el agente empieza en (1,1) y ahi no hay pozo ni wumpus
        self.decir([-id_var("Well", 1, 1)])
        self.decir([-id_var("Wumpus", 1, 1)])

    def decir(self, clausula):
        """DECIR: anade una clausula (lista de literales) a la BC."""
        self.clausulas.append(clausula)

    def decir_percepcion(self, x, y, breeze, reek):
        """DECIR de lo percibido al llegar a la casilla (x, y)."""
        b_var = id_var("Breeze", x, y)
        r_var = id_var("Reek", x, y)
        self.decir([b_var if breeze else -b_var])
        self.decir([r_var if reek else -r_var])
        # El agente sigue vivo en (x, y): confirma que no hay pozo ni wumpus ahi
        self.decir([-id_var("Well", x, y)])
        self.decir([-id_var("Wumpus", x, y)])

    def implica(self, literal):
        """PREGUNTAR: comprueba si BC |= literal por refutacion."""
        clausulas_ampliadas = self.clausulas + [[-literal]]
        sat, _ = satisfacible(clausulas_ampliadas)
        return not sat

    def es_seguro(self, x, y):
        """Una casilla (x, y) es segura si se puede DEMOSTRAR que no hay
        pozo ni wumpus, es decir, si BC |= ¬Well(x,y) y BC |= ¬Wumpus(x,y)."""
        sin_pozo = self.implica(-id_var("Well", x, y))
        sin_wumpus = self.implica(-id_var("Wumpus", x, y))
        return sin_pozo and sin_wumpus

    def es_peligroso(self, x, y):
        """Una casilla se conoce como peligrosa si BC implica que hay pozo
        o que hay wumpus (no es lo mismo que 'no segura': puede ser
        simplemente desconocida)."""
        hay_pozo = self.implica(id_var("Well", x, y))
        hay_wumpus = self.implica(id_var("Wumpus", x, y))
        return hay_pozo or hay_wumpus

    def casillas_seguras_no_visitadas(self, x, y, visitadas):
        """Devuelve, de las vecinas de (x, y), las que la BC demuestra
        seguras y que aun no se han visitado."""
        vecinos = get_neighbors(x, y, self.N)
        return [
            (vx, vy) for vx, vy in vecinos
            if (vx, vy) not in visitadas and self.es_seguro(vx, vy)
        ]
