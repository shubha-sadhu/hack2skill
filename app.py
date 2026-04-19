from fastapi import FastAPI
from pydantic import BaseModel
from ml_predict import Model, Data
from final_predict import process_ai_risks, deliver_final_verdict

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models once at startup
clf_model = Model("model_delay_flag.pkl", "classifier_features.pkl")
reg_model = Model("model_delay_time.pkl", "regressor_features.pkl")


class ShipmentInput(BaseModel):
    Shipping_Mode: str
    Order_Status: str
    Days_for_shipment_scheduled: int
    order_weekday: int
    order_month: int
    Order_Item_Quantity: int
    Sales: float
    Order_Item_Profit_Ratio: float
    Latitude: float
    Longitude: float
    Customer_Country: str
    Order_Country: str


@app.get("/health")
def health():
    try:
        clf_model.model
        reg_model.model
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}

@app.get("/")
def home():
    return {"message": "Supply Chain AI API Running"}


@app.post("/predict")
def predict(data: ShipmentInput):

    input_dict = {
        "Shipping Mode": data.Shipping_Mode,
        "Order Status": data.Order_Status,
        "Days for shipment (scheduled)": data.Days_for_shipment_scheduled,
        "order_weekday": data.order_weekday,
        "order_month": data.order_month,
        "Order Item Quantity": data.Order_Item_Quantity,
        "Sales": data.Sales,
        "Order Item Profit Ratio": data.Order_Item_Profit_Ratio,
        "Latitude": data.Latitude,
        "Longitude": data.Longitude,
        "Customer Country": data.Customer_Country,
        "Order Country": data.Order_Country
    }

    shipment_data = Data.from_dict(input_dict)

    disruptions = process_ai_risks(shipment_data)

    result = deliver_final_verdict(
        shipment_data,
        disruptions,
        clf_model,
        reg_model
    )

    return result[0]

@app.post("/predict-batch")
def predict_batch(data: list[ShipmentInput]):

    shipment_data = Data.from_objects(data)

    disruptions = process_ai_risks(shipment_data)

    return deliver_final_verdict(
        shipment_data,
        disruptions,
        clf_model,
        reg_model
    )
