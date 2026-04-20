import pandas as pd
import numpy as np

my_list = ['air', 'road', 'rail', 'sea']
supplier=['A', 'B', 'C', 'D', 'E', 'F', 'G']
supplier_score=[0.166, 0.33, 0.498, 0.664, 0.83, 0.996]

df=pd.read_csv('Europe_supply_chain.csv')
df["Transport_mode"]=np.random.choice(my_list, len(df))
df["Supplier"]=np.random.choice(supplier, len(df))
df["Inventory_days"]=df["Category Id"]%20
df["Supplier_score"]=np.random.choice(supplier_score, len(df))

df.to_csv("Europe_supply_chain.csv", index=False)
