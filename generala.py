
import random
import csv
from collections import Counter

# ==========================================
# 1. CONFIGURACION DEL EXPERIMENTO
# ==========================================

NUM_ENFRENTAMIENTOS = 500
NUM_DADOS = 5
MAX_LANZAMIENTOS = 3

# Semilla para poder repetir el experimento
random.seed(20261121)

ESTRATEGIAS = ["Probabilistica", "Aleatoria"]

CATEGORIAS = [
    "1", "2", "3", "4", "5", "6",
    "Escalera_corta",
    "Escalera_larga",
    "Full",
    "Poker",
    "Generala"
]

# ==========================================
# 2. LANZAMIENTO DE DADOS
# ==========================================

def lanzar_dados(cantidad):
    return [random.randint(1, 6) for _ in range(cantidad)]


# ==========================================
# 3. IDENTIFICAR COMBINACIONES
# ==========================================

def combinaciones(dados):

    valores = set(dados)
    frecuencias = Counter(dados)

    escalera_corta = any(
        set(secuencia).issubset(valores)
        for secuencia in [
            [1, 2, 3, 4],
            [2, 3, 4, 5],
            [3, 4, 5, 6]
        ]
    )

    escalera_larga = (
        {1, 2, 3, 4, 5}.issubset(valores)
        or {2, 3, 4, 5, 6}.issubset(valores)
    )

    full = sorted(frecuencias.values()) == [2, 3]

    poker = 4 in frecuencias.values()

    generala = 5 in frecuencias.values()

    return {
        "Escalera_corta": escalera_corta,
        "Escalera_larga": escalera_larga,
        "Full": full,
        "Poker": poker,
        "Generala": generala
    }


# ==========================================
# 4. ESTRATEGIA ALEATORIA
# ==========================================

def conservar_aleatorio(dados):

    cantidad = random.randint(0, len(dados))

    posiciones = random.sample(
        range(len(dados)),
        cantidad
    )

    return posiciones


# ==========================================
# 5. ESTRATEGIA PROBABILISTICA
# ==========================================

def conservar_probabilistico(dados, categoria):

    frecuencias = Counter(dados)

    # Para las categorias numericas:
    # conserva los dados que tienen el numero buscado.

    if categoria in ["1", "2", "3", "4", "5", "6"]:

        numero = int(categoria)

        return [
            i for i, dado in enumerate(dados)
            if dado == numero
        ]

    # Para poker y generala:
    # conserva los dados del numero mas repetido.

    if categoria in ["Poker", "Generala"]:

        objetivo = max(
            frecuencias,
            key=frecuencias.get
        )

        return [
            i for i, dado in enumerate(dados)
            if dado == objetivo
        ]

    # Para escalera corta o larga:
    # conserva los valores que pertenecen
    # a la mejor secuencia disponible.

    if categoria in ["Escalera_corta", "Escalera_larga"]:

        if categoria == "Escalera_corta":
            secuencias = [
                [1, 2, 3, 4],
                [2, 3, 4, 5],
                [3, 4, 5, 6]
            ]
        else:
            secuencias = [
                [1, 2, 3, 4, 5],
                [2, 3, 4, 5, 6]
            ]

        mejor = max(
            secuencias,
            key=lambda secuencia: sum(
                1 for numero in secuencia
                if numero in dados
            )
        )

        posiciones = []
        utilizados = set()

        for i, dado in enumerate(dados):
            if dado in mejor and dado not in utilizados:
                posiciones.append(i)
                utilizados.add(dado)

        return posiciones

    # Para Full:
    # intenta conservar tres dados de un valor
    # y dos de otro valor.

    if categoria == "Full":

        valores = sorted(
            frecuencias,
            key=lambda x: frecuencias[x],
            reverse=True
        )

        if len(valores) >= 2:

            principal = valores[0]
            secundario = valores[1]

            posiciones = []

            for i, dado in enumerate(dados):
                if dado == principal and posiciones.count(i) < 3:
                    if sum(
                        1 for p in posiciones
                        if dados[p] == principal
                    ) < 3:
                        posiciones.append(i)

                elif dado == secundario:
                    if sum(
                        1 for p in posiciones
                        if dados[p] == secundario
                    ) < 2:
                        posiciones.append(i)

            return posiciones

        # Si todos son iguales, conserva tres.
        return [0, 1, 2]

    return []


# ==========================================
# 6. CALCULAR LOS PUNTOS DE CADA CATEGORIA
# ==========================================

def calcular_puntos(dados, categoria):

    frecuencia = Counter(dados)

    if categoria in ["1", "2", "3", "4", "5", "6"]:

        numero = int(categoria)

        return sum(
            dado for dado in dados
            if dado == numero
        )

    resultados = combinaciones(dados)

    if categoria == "Escalera_corta":
        return 20 if resultados[categoria] else 0

    if categoria == "Escalera_larga":
        return 30 if resultados[categoria] else 0

    if categoria == "Full":
        return 30 if resultados[categoria] else 0

    if categoria == "Poker":
        return 45 if resultados[categoria] else 0

    if categoria == "Generala":
        return 50 if resultados[categoria] else 0

    return 0


# ==========================================
# 7. JUGAR UNA PARTIDA
# ==========================================

def jugar_partida(estrategia):

    puntaje_total = 0
    suma_superior = 0

    primera_suma_dados = None
    jugadas_servidas = 0

    combinaciones_obtenidas = {
        "Escalera_corta": 0,
        "Escalera_larga": 0,
        "Full": 0,
        "Poker": 0,
        "Generala": 0
    }

    # Se juegan las 11 categorias.

    for turno, categoria in enumerate(CATEGORIAS):

        dados = lanzar_dados(NUM_DADOS)

        # Registrar la suma del primer lanzamiento
        # del primer turno.

        if turno == 0:
            primera_suma_dados = sum(dados)

        # Registrar combinaciones conseguidas
        # directamente en el primer lanzamiento
        # de cada turno.

        if turno == 0 or True:

            resultado_inicial = combinaciones(dados)

            jugadas_servidas += sum(
                resultado_inicial.values()
            )

        # Se permiten hasta tres lanzamientos.

        for lanzamiento in range(1, MAX_LANZAMIENTOS):

            if estrategia == "Aleatoria":

                posiciones = conservar_aleatorio(dados)

            else:

                posiciones = conservar_probabilistico(
                    dados,
                    categoria
                )

            dados_conservados = [
                dados[i] for i in posiciones
            ]

            cantidad_nuevos = (
                NUM_DADOS - len(dados_conservados)
            )

            nuevos_dados = lanzar_dados(cantidad_nuevos)

            dados = dados_conservados + nuevos_dados

        # Calcular los puntos de la categoria.

        puntos = calcular_puntos(dados, categoria)

        puntaje_total += puntos

        if categoria in ["1", "2", "3", "4", "5", "6"]:
            suma_superior += puntos

        # Registrar si se obtuvo la combinacion
        # correspondiente al turno.

        if categoria in combinaciones_obtenidas:
            if puntos > 0:
                combinaciones_obtenidas[categoria] = 1

    # Bono de 35 puntos si la suma superior
    # alcanza al menos 63 puntos.

    bonificacion = 35 if suma_superior >= 63 else 0

    puntaje_total += bonificacion

    return {
        "Estrategia": estrategia,
        "Puntos_acumulados": puntaje_total,
        "Primera_suma_dados": primera_suma_dados,
        "Jugadas_servidas": jugadas_servidas,
        "Escalera_corta": combinaciones_obtenidas["Escalera_corta"],
        "Escalera_larga": combinaciones_obtenidas["Escalera_larga"],
        "Full": combinaciones_obtenidas["Full"],
        "Poker": combinaciones_obtenidas["Poker"],
        "Generala": combinaciones_obtenidas["Generala"],
        "Bonificacion_obtenida": bonificacion
    }


# ==========================================
# 8. SIMULAR LOS ENFRENTAMIENTOS
# ==========================================

datos = []

for enfrentamiento in range(1, NUM_ENFRENTAMIENTOS + 1):

    # Cada enfrentamiento tiene un jugador
    # probabilistico y uno aleatorio.

    jugador_probabilistico = jugar_partida(
        "Probabilistica"
    )

    jugador_aleatorio = jugar_partida(
        "Aleatoria"
    )

    puntaje_probabilistico = (
        jugador_probabilistico["Puntos_acumulados"]
    )

    puntaje_aleatorio = (
        jugador_aleatorio["Puntos_acumulados"]
    )

    # Determinar el ganador.

    if puntaje_probabilistico > puntaje_aleatorio:

        resultado_probabilistico = 1
        resultado_aleatorio = 0

    elif puntaje_aleatorio > puntaje_probabilistico:

        resultado_probabilistico = 0
        resultado_aleatorio = 1

    else:

        # Empate: se deja vacío para representar NA.

        resultado_probabilistico = ""
        resultado_aleatorio = ""

    # Guardar los resultados de ambos jugadores.

    for jugador, resultado in [
        (jugador_probabilistico, resultado_probabilistico),
        (jugador_aleatorio, resultado_aleatorio)
    ]:

        fila = {
            "ID_enfrentamiento": enfrentamiento,
            **jugador,
            "Resultado_partida": resultado
        }

        datos.append(fila)


# ==========================================
# 9. EXPORTAR LOS DATOS A CSV
# ==========================================

columnas = [
    "ID_enfrentamiento",
    "Estrategia",
    "Puntos_acumulados",
    "Primera_suma_dados",
    "Jugadas_servidas",
    "Escalera_corta",
    "Escalera_larga",
    "Full",
    "Poker",
    "Generala",
    "Bonificacion_obtenida",
    "Resultado_partida"
]

with open(
    "resultados_generala.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as archivo:

    escritor = csv.DictWriter(
        archivo,
        fieldnames=columnas
    )

    escritor.writeheader()
    escritor.writerows(datos)


# ==========================================
# 10. RESUMEN DEL EXPERIMENTO
# ==========================================

print("SIMULACION FINALIZADA")
print("------------------------------")

print("Enfrentamientos:", NUM_ENFRENTAMIENTOS)
print("Observaciones:", len(datos))

victorias_probabilisticas = sum(
    1 for fila in datos
    if fila["Estrategia"] == "Probabilistica"
    and fila["Resultado_partida"] == 1
)

victorias_aleatorias = sum(
    1 for fila in datos
    if fila["Estrategia"] == "Aleatoria"
    and fila["Resultado_partida"] == 1
)

empates = sum(
    1 for fila in datos
    if fila["Resultado_partida"] == ""
) // 2

print("Victorias probabilisticas:", victorias_probabilisticas)
print("Victorias aleatorias:", victorias_aleatorias)
print("Empates:", empates)

print("------------------------------")
print("Archivo creado: resultados_generala.csv")

