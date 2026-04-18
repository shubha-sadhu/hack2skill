import requests

r = requests.post(
    "http://127.0.0.1:8000/predict",
    json={
        "Shipping_Mode": "Second Class",
        "Order_Status": "PENDING_PAYMENT",
        "Days_for_shipment_scheduled": 3,
        "order_weekday": 2,
        "order_month": 7,
        "Order_Item_Quantity": 3,
        "Sales": 299.97,
        "Order_Item_Profit_Ratio": 0.44,
        "Latitude": 18.35,
        "Longitude": -66.07,
        "Customer_Country": "Puerto Rico",
        "Order_Country": "Germany"
    }
)

print(r.json())