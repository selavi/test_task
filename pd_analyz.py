import pandas as pd


df = pd.read_csv('parsed_data.txt', header=None)

print(df.iloc[:, 2].value_counts())
