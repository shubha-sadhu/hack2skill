# 📦 Supply Chain Delay & Risk Prediction System

## 🚀 Overview

This project is a hybrid **Machine Learning + AI-driven risk assessment system** designed to predict shipment delays and assess external risks affecting supply chains.

Requires Python >=3.12

It combines:

* **ML models** for internal delay prediction
* **LLM-powered analysis (Gemini API)** for real-time external disruptions
* A **fusion scoring system** to produce a final risk score

---

## 🧠 Core Idea

Traditional models only consider historical data.
This system enhances predictions by incorporating:

* 📊 **Historical patterns (ML)**
* 🌍 **Real-world events (AI + news analysis)**

---

## 🏗️ Architecture

```
Input Data (CSV / DB / Dict)
        ↓
   Data Wrapper (Data class)
        ↓
   ┌───────────────┬────────────────┐
   │               │                │
ML Classifier   ML Regressor   Gemini AI
(Delay Flag)    (Delay Days)   (External Risk)
   │               │                │
   └─────── Fusion Layer ──────────┘
                ↓
        Final Risk Score
```

---

## 🔍 Features

### ✅ 1. Delay Prediction (ML)

* **Classifier** → Predicts if delay will occur
* **Regressor** → Predicts delay duration (only if delay is expected)

### ✅ 2. External Risk Analysis (AI)

* Uses Gemini API with Google Search tool
* Extracts:

  * Geopolitical risks
  * Weather disruptions
  * Labor strikes
  * Infrastructure issues
* Maps them to:

  * Severity (`low`, `medium`, `high`)
  * Transport modes (`air`, `road`, `sea`, `rail`)

---

### ✅ 3. Route-Based Risk Mapping

* Routes are represented using:

```python
frozenset([Customer Country, Order Country])
```

* Ensures:

```plaintext
A → B == B → A
```

---

### ✅ 4. Risk Scoring Logic

#### 🔹 ML Output

```python
expected_delay = delay_probability * delay_days
```

#### 🔹 External Risk

```python
risk = severity_score × max(mode_confidence)
```

#### 🔹 Final Score

```python
final_score = (
    0.6 * delay_probability +
    0.2 * normalized_delay_days +
    0.2 * external_risk
)
```

---

## 📂 Project Structure

```
.
├── ml_predict.py              # ML Model & Data wrapper
├── gemini_external_risk_assessment.py
├── main_pipeline.py           # Core pipeline (this file)
├── model_delay_flag.pkl
├── model_delay_time.pkl
├── classifier_features.pkl
├── regressor_features.pkl
├── Europe_supply_chain.csv
└── README.md
```

---

## Quick Links

- [Local Setup](local_setup_supply_chain_api.md)

## ⚙️ Key Components

### 🔹 `Data` Class

* Handles:

  * DataFrame storage
  * One-hot encoding
  * Feature alignment

### 🔹 `Model` Class

* Wraps:

  * Loaded ML models
  * Prediction methods

### 🔹 `AI_Model` Class

* Wrapper over Gemini API
* Supports:

  * Google Search integration
  * JSON extraction with retry logic

---

## 🔁 Pipeline Flow

### 1. Preprocess Input

```python
data = Data(dataframe=df)
```

### 2. Extract Unique Routes

```python
routes = set(frozenset([c1, c2]))
```

### 3. Fetch External Risks

```python
disruption_dict = process_ai_risks(data)
```

### 4. Predict Delay + Risk

```python
results = deliver_final_verdict(...)
```

---

## 🧪 Example Output

```json
[
  {
    "will_delay": 1,
    "delay_probability": 0.73,
    "delay_days": 4.2,
    "expected_delay": 3.06,
    "external_risk": 0.6,
    "final_risk_score": 0.69
  }
]
```

---

## ⚠️ Design Considerations

### 🔸 Defensive Programming

* Handles:

  * Missing keys
  * Invalid JSON from AI
  * Empty responses

### 🔸 Separation of Concerns

* ML logic independent from AI logic
* Data object remains immutable across transformations

### 🔸 Runtime Safety

* Uses `.get()` for dynamic inputs
* Avoids crashes from malformed data

---

## 🚧 Current Limitations

* ⏳ Gemini API latency (real-time calls)
* 📉 No caching for repeated routes
* 🧪 Limited batch optimization
* 📊 External risk assumes latest news relevance

---

## 🔮 Future Improvements

* ✅ Caching external risk per route
* ⏱️ Time-decay for news relevance
* 📊 Confidence-weighted risk scoring
* ⚡ Async API calls for performance
* 🌐 Deployment as a scalable API service

---

## 🏁 Conclusion

This system moves beyond traditional ML by integrating **real-world dynamic risk signals**, making it more suitable for modern supply chain applications.

---

## 💬 Key Insight

> *“Prediction without context is incomplete — this system brings context into prediction.”*
