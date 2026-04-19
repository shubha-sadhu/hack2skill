from pydantic import BaseModel

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