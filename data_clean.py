import pandas as pd
df = pd.read_csv('Europe_supply_chain.csv')
df = df.drop(columns=[
    'Customer Email', 'Customer Password', 'Product Image', 'Unnamed: 0'
])
df = pd.get_dummies(df, columns=[
    'Shipping Mode',
    'Customer Segment',
    'Customer Country',
    'Customer City',
    'Order Country',
    'Order City',
    'Order Status'
])
#df['delay_days'] = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
#df['order_date'] = pd.to_datetime(df['order date (DateOrders)'], format='%m/%d/%Y %H:%M')
#df['ship_date'] = pd.to_datetime(df['shipping date (DateOrders)'], format='%m/%d/%Y %H:%M')

df['order_date_1'] = pd.to_datetime(
    df['order date (DateOrders)'],
    dayfirst=True,
    errors='coerce'
)

df['ship_date_1'] = pd.to_datetime(
    df['shipping date (DateOrders)'],
    dayfirst=True,
    errors='coerce'
)

df['order_date_2'] = pd.to_datetime(
    df['order date (DateOrders)'],
    dayfirst=False,
    errors='coerce'
)

df['ship_date_2'] = pd.to_datetime(
    df['shipping date (DateOrders)'],
    dayfirst=False,
    errors='coerce'
)

df['order_date'] = df['order_date_1'].fillna(df['order_date_2'])
df['ship_date'] = df['ship_date_1'].fillna(df['ship_date_2'])

df.drop(columns=[
    'order_date_1', 'order_date_2',
    'ship_date_1', 'ship_date_2'
], inplace=True)

df['processing_time'] = (df['ship_date'] - df['order_date']).dt.days
df['delay_days'] = df['processing_time'] - df['Days for shipment (scheduled)']
df['delay_flag'] = (df['delay_days'] > 0).astype(int)
df['order_day'] = df['order_date'].dt.day
df['order_month'] = df['order_date'].dt.month
df['order_weekday'] = df['order_date'].dt.weekday
df['order_year']=df['order_date'].dt.year

print(df['processing_time'].describe())

print(df[['ship_date', 'order_date', 'processing_time', 'Days for shipping (real)', 'delay_days']])
df.to_csv('Europe_chain_data_modified.csv', index=False)