import joblib
import pandas as pd
from pathlib import Path
import magic
from io import BytesIO
# def predict(input_dict):
#     clf = joblib.load("model_delay_flag.pkl")
#     reg = joblib.load("model_delay_time.pkl")

#     clf_features = joblib.load("classifier_features.pkl")
#     reg_features = joblib.load("regressor_features.pkl")

#     df = pd.DataFrame([input_dict])

#     for col in set(clf_features + reg_features):
#         if col not in df:
#             df[col] = 0

#     X_clf = df[clf_features]
#     X_reg = df[reg_features]

#     delay_flag = clf.predict(X_clf)[0]
#     delay_prob = clf.predict_proba(X_clf)[0][1]

#     delay_days = reg.predict(X_reg)[0]

#     return {
#         "will_delay": int(delay_flag),
#         "delay_probability": float(delay_prob),
#         "delay_days_if_delayed": float(delay_days),
#         "expected_delay": float(delay_prob * delay_days)
#     }

class Model(object):
    def __init__(self, model_pkl_file, features_pkl_file):
        self.model=joblib.load(model_pkl_file)
        self.features=joblib.load(features_pkl_file)

    def get_prediction(self, df):
        X=df[self.features]
        return self.model.predict(X)[0]
    
    def get_probability(self, df):
        X=df[self.features]
        return self.model.predict_proba(X)[0][1]

class Data(object):
    def __init__(self, filename=None, dataframe=None, databytes=None):
        self.filename=filename
        self.dataframe=dataframe
        self.databytes=databytes
    
    def _get_reader(self):
        """Private helper to map extensions to pandas functions."""
        reader_map = {
        ".csv": pd.read_csv,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".json": pd.read_json,
        ".parquet": pd.read_parquet,
        ".pkl": pd.read_pickle
        }

        if self.databytes is not None:
            mime = magic.from_buffer(self.databytes, mime=True)

            mime_map = {
                "text/csv": ".csv",
                "text/plain": ".csv",
                "application/csv": ".csv",
                "application/json": ".json",
                "application/vnd.ms-excel": ".xls",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx"
            }

            extension = mime_map.get(mime)

        elif self.filename is not None:
            extension = Path((self.filename).suffix.lower())

        else:
            extension = None

        return reader_map.get(extension)
        
    def extract_dataframe(self):
        # Get the function from the map
        reader = self._get_reader()
        if reader and self.databytes==None:
            return reader(self.filename)
        elif self.databytes!=None:
            if reader is None:
                raise ValueError("Unsupported file type")
            return reader(BytesIO(self.databytes))
        else:
            raise ValueError(f"Unsupported file extension: {self.filename}")
        
    def get_dataframe(self):
        if self.dataframe is not None:
            return self.dataframe

        if self.filename is not None or self.databytes is not None:
            self.dataframe = self.extract_dataframe()
            return self.dataframe

        raise ValueError("No data source provided")

    def one_hot_encode(self, categorical_tools):
        """
        :param categorical_tools: A list of the features that will undergo one-hot encoding
        Returns the dataframe with one-hot encoding of those features and after mutatin
        """
        df=self.get_dataframe()
        df=pd.get_dummies(df, columns=categorical_tools)
        return df
    
    def align_features(self, the_model):
        feature_list=the_model.features
        df = self.get_dataframe().copy()

        for col in feature_list:
            if col not in df:
                df[col] = 0

        return df[feature_list]
    
    def prepare_for_model(self, model, categorical_cols=None):
        df = self.get_dataframe()
        if categorical_cols:
            df = pd.get_dummies(df, columns=categorical_cols)
        df = Data(dataframe=df).align_features(model)

        return df

    @classmethod
    def from_db(cls, query, db_connection):
        """Extracts directly to memory without touching the hard drive."""
        df = pd.read_sql(query, db_connection)
        return cls(dataframe=df) # Passes the DataFrame object directly to __init__
    
    @classmethod
    def from_dict(cls, input_dict):
        """        
        :param cls: The Class
        :param input_dict: A dictionary of the features as keys and their values
        => Returns a 'Data' object initialized with the pandas dataframe object obtained
           from input_dict
        """
        df=pd.DataFrame([input_dict])
        return cls(dataframe=df)
    
    @classmethod
    def from_objects(cls, items):
        payloads = [
            obj.model_dump() if hasattr(obj, "model_dump") else obj
            for obj in items
        ]

        rows=[]
        for data in payloads:
            rows.append({
                "Shipping Mode": data.get("Shipping_Mode"),
                "Order Status": data.get("Order_Status"),
                "Days for shipment (scheduled)": data.get("Days_for_shipment_scheduled"),
                "order_weekday": data.get("order_weekday"),
                "order_month": data.get("order_month"),
                "Order Item Quantity": data.get("Order_Item_Quantity"),
                "Sales": data.get("Sales"),
                "Order Item Profit Ratio": data.get("Order_Item_Profit_Ratio"),
                "Latitude": data.get("Latitude"),
                "Longitude": data.get("Longitude"),
                "Customer Country": data.get("Customer_Country"),
                "Order Country": data.get("Order_Country")
            })

        df = pd.DataFrame(rows)
        return cls(dataframe=df)
    
    @classmethod
    def from_upload(cls, upload_file):
        file_bytes = upload_file.file.read()
        extension=magic.from_buffer(file_bytes, mime=True)
        print(extension)
        ALLOWED = (
            "application/csv",
            "text/csv",
            "text/plain",
            "application/json",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "application/octet-stream"
        )

        if extension in ALLOWED:
            data=Data(databytes=file_bytes)
            df=data.get_dataframe()
            return cls(dataframe=df)
        else:
            raise TypeError('Not a valid filetype')
    

if __name__=='__main__':
    test_input = {
    'Days for shipment (scheduled)': 5,
    'Shipping Mode': 'Standard Class',
    'order_weekday': 2,
    'order_month': 7,
    'Order Item Quantity': 3,
    'Sales': 200,
    'Order Item Profit Ratio': 0.2,
    'Latitude': 40.0,
    'Longitude': -3.0,
    'Order Status': 'PROCESSING'
    }
    # 'Order Status_CANCELED':0, 
    # 'Order Status_CLOSED':0, 
    # 'Order Status_COMPLETE':0, 
    # 'Order Status_ON_HOLD':0, 
    # 'Order Status_PAYMENT_REVIEW':0, 
    # 'Order Status_PENDING':0, 
    # 'Order Status_PENDING_PAYMENT':0, 
    # 'Order Status_PROCESSING':1, 
    # 'Order Status_SUSPECTED_FRAUD':0

    clf_model=Model("model_delay_flag.pkl", "classifier_features.pkl")
    reg_model=Model("model_delay_time.pkl", "regressor_features.pkl")
    test_data=Data.from_dict(test_input)
    clf_data=test_data.prepare_for_model(clf_model, ['Order Status', 'Shipping Mode'])
    reg_data=test_data.prepare_for_model(reg_model)
    #reg_data.dataframe=reg_data.one_hot_encode(['Order Status'])
    #print(the_df.head)

    print(f"Will It be delayed: {clf_model.get_prediction(clf_data)}")
    print(f"Delay probability: {clf_model.get_probability(clf_data)}")
    print(f"Days of delay: {reg_model.get_prediction(reg_data)}")