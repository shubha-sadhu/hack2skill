
# Local Setup Guide – Supply Chain API

## Overview

This guide explains how to download the repository and run the API service locally.

---

## 1. Clone the Repository

```bash
git clone https://github.com/samsahu2007/hack2skill.git
cd hack2skill
```

---

## 2. Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If requirements.txt is missing:

```bash
pip install fastapi[standard] uvicorn pandas scikit-learn python-dotenv google-genai openpyxl
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_api_key_here (Create your own API key from Google AI Studio. It is free of cost)
```

---

## 5. Start the API Server

```bash
uvicorn app:app --reload
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

## 6. Use the API Locally

### Swagger Docs

Open in browser:

```text
http://127.0.0.1:8000/docs
```

### Health Check

```text
http://127.0.0.1:8000/health
```

---

## 7. Example Prediction Request

### POST `/predict`

```json
{
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
```

Use `/docs` to send this request directly.

---

## 8. Common Issues

### Port Already in Use

```bash
lsof -i :8000
kill -9 <PID>
```

### Missing Module Errors

```bash
pip install -r requirements.txt
```

### Invalid API Key

Update `.env` with a valid key and restart server.

---

## 9. Stop the Server

Press:

```text
Ctrl + C
```

---

## 10. Recommended Development Workflow

Terminal 1:

```bash
uvicorn app:app --reload
```

Terminal 2:

Use scripts, Postman, frontend, or testing tools.

---

## 11. Notes for Contributors

- Do not commit `.env`
- Keep secrets private
- Use feature branches
- Test `/health` before debugging deeper issues
- Europe_supply_chain.csv is the data over which the model was trained. You can use 
  it for testing the API or for your own purpose
