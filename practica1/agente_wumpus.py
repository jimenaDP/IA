"""Bucle del agente logico para el mundo de Wumpus (patron AGENTE-WUMPUS-LP,
fig. 7.19): en cada paso, DECIR la percepcion actual y PREGUNTAR si las
casillas vecinas son seguras, para decidir el siguiente movimiento.

Este modulo no depende de pygame/gymnasium: usa generate_table() directamente
para poder ejecutar y depurar la logica del agente de forma aislada. La
integracion visual (RenderizadoTabla.py) puede llamar a estas mismas
funciones para dibujar cada paso.
"""

from GeneracionTablero import generate_table
from GeneracionNormas import get_neighbors
from agente_logico import BaseConocimiento


def ejecutar_agente(N=4, prob_well=0.3, verbose=True, semilla=None):
    """Ejecuta el agente sobre un tablero generado aleatoriamente.

    Devuelve (exito, pasos, visitadas, bc) para poder inspeccionar
    el resultado y la base de conocimiento final desde fuera.
    """
    if semilla is not None:
        import random
        random.seed(semilla)

    tablero, posicion = generate_table(N=N, prob_well=prob_well)
    bc = BaseConocimiento(N)

    visitadas = set()
    x, y = posicion
    pasos = 0
    max_pasos = N * N * 2  # margen de seguridad para evitar bucles infinitos

    while pasos < max_pasos:
        pasos += 1
        visitadas.add((x, y))
        estado = tablero[(x, y)]

        if verbose:
            print(f"\nPaso {pasos}: agente en {(x, y)}")

        if estado["Gold"]:
            if verbose:
                print("¡Oro encontrado! El agente recoge el objetivo.")
            return True, pasos, visitadas, bc

        if estado["Well"] or estado["Wumpus"]:
            if verbose:
                print("El agente ha muerto (pozo o Wumpus).")
            return False, pasos, visitadas, bc

        # DECIR: registra lo percibido en la casilla actual
        bc.decir_percepcion(x, y, estado["Breeze"], estado["Reek"])

        # PREGUNTAR: de las vecinas, cuales demuestra la BC que son seguras
        seguras = bc.casillas_seguras_no_visitadas(x, y, visitadas)

        if verbose:
            print(f"Percepcion: Brisa={estado['Breeze']}, Hedor={estado['Reek']}")
            print(f"Casillas vecinas deducidas como seguras: {seguras}")

        if seguras:
            x, y = seguras[0]
        else:
            no_visitadas = [
                (vx, vy) for vx, vy in get_neighbors(x, y, N)
                if (vx, vy) not in visitadas
            ]
            if not no_visitadas:
                if verbose:
                    print("No quedan casillas nuevas alcanzables. El agente se detiene.")
                return False, pasos, visitadas, bc
            if verbose:
                print("Ninguna vecina es segura todavia. El agente arriesga un movimiento.")
            x, y = no_visitadas[0]

    if verbose:
        print("Limite de pasos alcanzado sin encontrar el oro.")
    return False, pasos, visitadas, bc


if __name__ == "__main__":
    exito, pasos, visitadas, bc = ejecutar_agente(N=4, prob_well=0.3, semilla=1)
    print(f"\nResultado final: {'EXITO' if exito else 'FALLO'} en {pasos} pasos")
    print(f"Casillas visitadas: {sorted(visitadas)}")
