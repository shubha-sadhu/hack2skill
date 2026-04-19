# from fastapi import FastAPI, UploadFile, HTTPException, File
# from app.core.ml_model import Model
# from app.core.data import Data
# from app.schema.shipment import ShipmentInput
# from app.services.final_predict import process_ai_risks, deliver_final_verdict
# from typing import Optional
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent
# MODEL_DIR = BASE_DIR / "models"

# app = FastAPI()

# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load models once at startup
# clf_model = Model(str(MODEL_DIR / "model_delay_flag.pkl"),
#         str(MODEL_DIR / "classifier_features.pkl")
#     )
# reg_model = Model(str(MODEL_DIR / "model_delay_time.pkl"),
#         str(MODEL_DIR / "regressor_features.pkl")
#     )

# @app.get("/health")
# def health():
#     try:
#         clf_model.model
#         reg_model.model
#         return {"status": "ok"}
#     except Exception:
#         return {"status": "error"}

# @app.get("/")
# def home():
#     return {"message": "Supply Chain AI API Running"}


# @app.post("/predict")
# def predict(data: ShipmentInput):

#     input_dict = {
#         "Shipping Mode": data.Shipping_Mode,
#         "Order Status": data.Order_Status,
#         "Days for shipment (scheduled)": data.Days_for_shipment_scheduled,
#         "order_weekday": data.order_weekday,
#         "order_month": data.order_month,
#         "Order Item Quantity": data.Order_Item_Quantity,
#         "Sales": data.Sales,
#         "Order Item Profit Ratio": data.Order_Item_Profit_Ratio,
#         "Latitude": data.Latitude,
#         "Longitude": data.Longitude,
#         "Customer Country": data.Customer_Country,
#         "Order Country": data.Order_Country
#     }

#     shipment_data = Data.from_dict(input_dict)

#     disruptions = process_ai_risks(shipment_data)

#     result = deliver_final_verdict(
#         shipment_data,
#         disruptions,
#         clf_model,
#         reg_model
#     )

#     return result[0]

# @app.post("/predict-batch-file")
# async def predict_batch_file(
#     file: Optional[UploadFile] = File(default=None)
# ):
#     try:
#         shipment_data = Data.from_upload(file)

#         disruptions = process_ai_risks(shipment_data)

#         return deliver_final_verdict(
#             shipment_data,
#             disruptions,
#             clf_model,
#             reg_model
#         )
    
#     except Exception as e:
#         raise HTTPException(status_code=422, detail=str(e))
