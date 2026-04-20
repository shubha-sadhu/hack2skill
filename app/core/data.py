import pandas as pd
from pathlib import Path
import magic
from io import BytesIO

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
            print(df.dtypes)
            print(df.head())        
            return cls(dataframe=df)
        else:
            raise TypeError('Not a valid filetype')
