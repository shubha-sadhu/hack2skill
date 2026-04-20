# protecting existing api
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()
SECRET = "chainguard-secret-key"

# validating user
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schema.shipment import ShipmentInput
from app.core.data import Data
from app.core.ml_model import Model
from app.services.final_predict import deliver_final_verdict, process_ai_risks
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models"

clf_model = Model(str(MODEL_DIR / "model_delay_flag.pkl"),
        str(MODEL_DIR / "classifier_features.pkl")
    )
reg_model = Model(str(MODEL_DIR / "model_delay_time.pkl"),
        str(MODEL_DIR / "regressor_features.pkl")
    )

router = APIRouter()

@router.get("/health")
def health():
    try:
        clf_model.model
        reg_model.model
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}

@router.get("/")
def home():
    return {"message": "Supply Chain AI API Running"}


@router.post("/predict")
def predict(data: dict, user=Depends(get_current_user)):

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

@router.post("/predict-batch-file")
async def predict_batch_file(
    file: UploadFile = File(default=None)
):
    try:
        shipment_data = Data.from_upload(file)

        disruptions = process_ai_risks(shipment_data)

        return deliver_final_verdict(
            shipment_data,
            disruptions,
            clf_model,
            reg_model
        )
    
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


