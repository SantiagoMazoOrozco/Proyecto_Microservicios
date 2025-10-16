import pandas as pd

def assign_rounds_to_sets(df):
    """
    Asigna rondas a los sets de un torneo de doble eliminación, asumiendo que el último set es la Grand Final,
    el penúltimo es Winners Final, luego Losers Final, Winners Semifinal, etc.
    Esta función es solo una heurística y sirve para torneos pequeños o para uso manual.
    """
    # Ordena por el orden original del archivo (o por id_set si es incremental)
    df = df.reset_index(drop=True)
    n = len(df)
    rounds = ['Grand Final', 'Winners Final', 'Losers Final', 'Winners Semifinal', 'Losers Semifinal',
              'Winners Quarterfinal', 'Losers Quarterfinal']
    # Asigna las rondas desde el final hacia el principio
    ronda_col = [None] * n
    for i, round_name in enumerate(rounds):
        if n - 1 - i >= 0:
            ronda_col[n - 1 - i] = round_name
    # El resto los marca como "Bracket" o "Ronda Previa"
    for i in range(n - len(rounds)):
        ronda_col[i] = "Bracket"
    df['Ronda'] = ronda_col
    return df

# Ejemplo de uso:
if __name__ == "__main__":
    # Carga el archivo Excel
    df = pd.read_excel("sets.xlsx")
    df = assign_rounds_to_sets(df)
    df.to_excel("sets_con_rondas.xlsx", index=False)
