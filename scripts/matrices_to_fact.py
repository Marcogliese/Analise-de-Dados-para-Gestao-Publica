import pandas as pd

file = "Assunto_categoria.xlsx"
df = pd.read_excel(file)

coluna_x = df.columns[0]

# Convert a matrix X×Y to a table normalized (x, y, xy)
df_melt = df.melt(id_vars=coluna_x, var_name='y', value_name='xy')

# Add incremental ID starting at 1
df_melt.insert(0, 'id', range(1, len(df_melt) + 1))

df_melt.to_excel("table.xlsx", index=False)