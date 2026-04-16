from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
#from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
import joblib

df = pd.read_csv('Europe_chain_data_modified.csv')
# models = {
#     'Random Forest':
#    RandomForestRegressor(
#     n_estimators=200,
#     max_depth=10,
#     random_state=42),
# }

models = {
    "Gradient":GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    random_state=42)
}

# "Random Forest": RandomForestClassifier(n_estimators=300,
#     max_depth=12,
#     min_samples_split=10,
#     min_samples_leaf=5,
#     max_features='sqrt',
#     random_state=42),
#     "Decision Tree": DecisionTreeClassifier(max_depth=10,
#     min_samples_split=20,
#     min_samples_leaf=10,
#     random_state=42),

# Example: 1 kilometer radius (converted to radians for haversine)
# kms_per_radian = 6371.0
# epsilon = 1000.0 / kms_per_radian

# # Coordinates must be (lat, lon)
# coords = df[['Latitude', 'Longitude']].values

# # Run DBSCAN
# db = DBSCAN(eps=epsilon, min_samples=10, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
# #labels = db.labels_
# df['cluster_id'] = db.labels_
# n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
# n_noise = list(labels).count(-1)
#counts = pd.Series(db.labels_).value_counts().sort_index()

# print(f"Number of clusters found: {n_clusters}")
# print(f"Number of noise points: {n_noise}")
# print(counts)
#print(df['cluster'])

base_features = [
    'Shipping Mode_Second Class',
    'Shipping Mode_Standard Class',    
    'Order Item Quantity',
    'Sales',
    'order_weekday',
    'order_month',
    'Latitude',
    'Longitude',
    'Days for shipment (scheduled)',
    'Order Item Profit Ratio'
]
# base_features = [
#     'Shipping Mode_Second Class',
#     'Shipping Mode_Standard Class',    
#     'Order Item Quantity',
#     'order_weekday',
#     'order_month',
#     'Days for shipment (scheduled)',
# ]

#customer_labels = [col for col in df.columns if col.startswith('Customer Country_')]
#order_labels= [col for col in df.columns if col.startswith('Order Country_')]
order_status_labels= [col for col in df.columns if col.startswith('Order Status_')]

features = base_features + order_status_labels

X=df[features]
y = df['delay_flag']
#print(df['delay_flag'].value_counts())
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

for name, model in models.items():
    model.fit(X_train, y_train)
    print(name)
    print("Train accuracy:", model.score(X_train, y_train))
    print("Test accuracy:", model.score(X_test, y_test))
    importances = model.feature_importances_
    feat_imp = pd.Series(importances, index=X.columns)
    print(feat_imp.sort_values(ascending=False))
    print('')
    joblib.dump(model, "model_delay_flag.pkl")
    joblib.dump(features, "classifier_features.pkl")
    # score = model.score(X_test, y_test)
    # print(name, score)
    #print(classification_report(y_test, y))



new_features = [
    'Days for shipment (scheduled)',
    'Shipping Mode_Standard Class',
    'Shipping Mode_Second Class',
    'order_weekday',
    'order_month',
    'Order Item Quantity',
    'Sales',
    'Order Item Profit Ratio',
    'Latitude',
    'Longitude'
]
new_y = df['processing_time']
new_X=df[new_features]
X_train, X_test, y_train, y_test = train_test_split(
    new_X, new_y, test_size=0.2, random_state=42
)
model_regression = RandomForestRegressor(
    n_estimators=100,
    max_depth=12,
    max_features='sqrt',
    random_state=42
)

model_regression.fit(X_train, y_train)
joblib.dump(model_regression, "model_delay_time.pkl")
joblib.dump(new_features, "regressor_features.pkl")

y_pred = model_regression.predict(X_test)

print("MAE:", mean_absolute_error(y_test, y_pred))