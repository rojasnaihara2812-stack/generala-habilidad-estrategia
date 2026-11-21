
import random
import pandas as pd
from collections import Counter

# ==========================================
# PROYECTO: GENERALA TRADICIONAL
# Comparación de estrategias
# ==========================================

SEMILLA = 20261121
NUM_ENFRENTAMIENTOS = 500

rng = random.Random(SEMILLA)

CATEGORIAS = [
    1, 2, 3, 4, 5, 6,
    "Escalera_corta",
    "Escalera_larga",
    "Full",
    "Poker",
    "Generala"
]

PUNTOS_ESPECIALES = {
    "Escalera_corta": 20,
    "Escalera_larga": 30,
    "Full": 30,
    "Poker": 45,
    "Generala": 50
}


def lanzar_dados(cantidad):
    return [rng.randint(1, 6) for _ in range(cantidad)]


def evaluar_combinaciones(dados):
    valores = set(dados)
    frecuencias = Counter(dados)

    escalera_corta = any(
        set(range(inicio, inicio + 4)).issubset(valores)
        for inicio in range(1, 4)
    )

    escalera_larga = (
        len(valores) == 5 and
        valores in (
            {1, 2, 3, 4, 5},
            {2, 3, 4, 5, 6}
        )
    )

    return {
        "Escalera_corta": escalera_corta,
        "Escalera_larga": escalera_larga,
        "Full": sorted(frecuencias.values()) == [2, 3],
        "Poker": max(frecuencias.values()) >= 4,
        "Generala": max(frecuencias.values()) == 5
    }


def elegir_dados(dados, categoria, estrategia):

    if estrategia == "Aleatoria":
        cantidad = rng.randint(0, len(dados))
        return set(rng.sample(range(len(dados)), cantidad))

    if isinstance(categoria, int):
        return {
            i for i, dado in enumerate(dados)
            if dado == categoria
        }

    frecuencias = Counter(dados)

    if categoria in ("Escalera_larga", "Escalera_corta"):
        if categoria == "Escalera_larga":
            secuencias = [
                {1, 2, 3, 4, 5},
                {2, 3, 4, 5, 6}
            ]
        else:
            secuencias = [
                {1, 2, 3, 4},
                {2, 3, 4, 5},
                {3, 4, 5, 6}
            ]

        mejor = max(
            secuencias,
            key=lambda s: sum(d in s for d in dados)
        )

        return {
            i for i, d in enumerate(dados)
            if d in mejor
        }

    if categoria == "Full":
        grupos = sorted(
            frecuencias.items(),
            key=lambda x: x[1],
            reverse=True
        )

        valores_a_conservar = {grupos[0][0]}

        if len(grupos) >= 2 and grupos[0][1] == 3:
            if grupos[1][1] == 2:
                valores_a_conservar.add(grupos[1][0])

        return {
            i for i, d in enumerate(dados)
            if d in valores_a_conservar
        }

    valor = max(frecuencias, key=frecuencias.get)

    return {
        i for i, d in enumerate(dados)
        if d == valor
    }


def jugar_turno(categoria, estrategia):

    dados = lanzar_dados(5)

    primera_suma = sum(dados)

    combinaciones_iniciales = evaluar_combinaciones(dados)
    jugadas_servidas = sum(combinaciones_iniciales.values())

    for _ in range(2):
        conservar = elegir_dados(
            dados,
            categoria,
            estrategia
        )

        nuevos = lanzar_dados(5 - len(conservar))

        dados = [
            dado for i, dado in enumerate(dados)
            if i in conservar
        ] + nuevos

    return dados, primera_suma, jugadas_servidas


def calcular_puntos(dados, categoria):

    if isinstance(categoria, int):
        return sum(
            dado for dado in dados
            if dado == categoria
        )

    combinaciones = evaluar_combinaciones(dados)

    if combinaciones[categoria]:
        return PUNTOS_ESPECIALES[categoria]

    return 0


def jugar_partida(estrategia):

    puntos = 0
    suma_superior = 0
    jugadas_servidas = 0
    primera_suma_dados = None

    indicadores = {
        "Escalera_corta": 0,
        "Escalera_larga": 0,
        "Full": 0,
        "Poker": 0,
        "Generala": 0
    }

    for numero_turno, categoria in enumerate(CATEGORIAS):

        dados, primera_suma, servidas = jugar_turno(
            categoria,
            estrategia
        )

        if numero_turno == 0:
            primera_suma_dados = primera_suma

        jugadas_servidas += servidas

        puntos_turno = calcular_puntos(
            dados,
            categoria
        )

        puntos += puntos_turno

        if isinstance(categoria, int):
            suma_superior += puntos_turno
        else:
            indicadores[categoria] = int(
                evaluar_combinaciones(dados)[categoria]
            )

    bonificacion = 35 if suma_superior >= 63 else 0
    puntos += bonificacion

    return {
        "Estrategia": estrategia,
        "Puntos_acumulados": puntos,
        "Primera_suma_dados": primera_suma_dados,
        "Jugadas_servidas": jugadas_servidas,
        "Escalera_corta": indicadores["Escalera_corta"],
        "Escalera_larga": indicadores["Escalera_larga"],
        "Full": indicadores["Full"],
        "Poker": indicadores["Poker"],
        "Generala": indicadores["Generala"],
        "Bonificacion_obtenida": bonificacion,
        "Experiencia": "NA"
    }


# ==========================================
# RECOLECCIÓN DE DATOS
# ==========================================

registros = []

for enfrentamiento in range(1, NUM_ENFRENTAMIENTOS + 1):

    probabilistica = jugar_partida("Probabilistica")
    aleatoria = jugar_partida("Aleatoria")

    puntos_prob = probabilistica["Puntos_acumulados"]
    puntos_azar = aleatoria["Puntos_acumulados"]

    if puntos_prob > puntos_azar:
        resultado_prob, resultado_azar = 1, 0
    elif puntos_azar > puntos_prob:
        resultado_prob, resultado_azar = 0, 1
    else:
        resultado_prob, resultado_azar = None, None

    probabilistica["ID_enfrentamiento"] = enfrentamiento
    aleatoria["ID_enfrentamiento"] = enfrentamiento

    probabilistica["Resultado_partida"] = resultado_prob
    aleatoria["Resultado_partida"] = resultado_azar

    registros.extend([probabilistica, aleatoria])


# ==========================================
# CREACIÓN DE ARCHIVOS
# ==========================================

df = pd.DataFrame(registros)

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
    "Resultado_partida",
    "Experiencia"
]

df = df[columnas]

resumen = df.groupby("Estrategia").agg(
    Partidas=("ID_enfrentamiento", "count"),
    Promedio_puntos=("Puntos_acumulados", "mean"),
    Mediana_puntos=("Puntos_acumulados", "median"),
    Desviacion_estandar=("Puntos_acumulados", "std"),
    Promedio_jugadas_servidas=("Jugadas_servidas", "mean"),
    Victorias=("Resultado_partida", "sum")
).reset_index()

resumen["Porcentaje_victorias"] = (
    resumen["Victorias"] / NUM_ENFRENTAMIENTOS
) * 100

df.to_csv(
    "Resultados_Generala.csv",
    index=False,
    encoding="utf-8-sig"
)

with pd.ExcelWriter("Resultados_Generala.xlsx") as writer:
    df.to_excel(writer, sheet_name="Datos", index=False)
    resumen.to_excel(writer, sheet_name="Resumen", index=False)

print("SIMULACIÓN FINALIZADA")
print("Registros generados:", len(df))
print("\nRESUMEN:")
print(resumen.to_string(index=False))
