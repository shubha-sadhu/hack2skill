def generate_recommendations(
    predicted_delay,
    risk_level,
    shipment_priority,
    transport_mode,
    inventory_days_left,
    supplier_score,
    weather_risk=False,
    port_congestion=False,
    strike_risk=False,
    fuel_spike=False,
    customs_risk=False,
    demand_spike=False,
    route_risk=False
):
    actions = []

    # -------------------------
    # DELAY BASED RULES
    # -------------------------
    if predicted_delay > 7:
        actions.append("Critical delay expected: escalate to operations leadership.")

    if predicted_delay > 5:
        actions.append("Prepare contingency fulfillment plan.")

    if 3 <= predicted_delay <= 5:
        actions.append("Monitor shipment daily and notify stakeholders.")

    if predicted_delay < 2:
        actions.append("No major disruption expected.")

    # -------------------------
    # PRIORITY RULES
    # -------------------------
    if shipment_priority == "Same Day" and predicted_delay > 2:
        actions.append("Expedite shipment using premium logistics option.")

    if shipment_priority == "First Class" and predicted_delay > 3:
        actions.append("Prioritize unloading and last-mile dispatch.")

    if shipment_priority == "Standard Class" and predicted_delay > 4:
        actions.append("Reschedule delivery slot to reduce premium freight cost.")

    # -------------------------
    # INVENTORY RULES
    # -------------------------
    if predicted_delay > inventory_days_left:
        actions.append("Increase safety stock immediately to avoid stockout.")

    if inventory_days_left <= 3:
        actions.append("Trigger emergency replenishment review.")

    if inventory_days_left > 15:
        actions.append("Inventory buffer sufficient; avoid expensive expedite actions.")

    # -------------------------
    # SUPPLIER RULES
    # -------------------------
    if supplier_score < 0.50:
        actions.append("Supplier reliability low: shift future orders to alternate vendor.")

    if supplier_score < 0.30:
        actions.append("Freeze non-critical purchase orders from this supplier.")

    if supplier_score > 0.85:
        actions.append("Preferred supplier available: consider volume reallocation.")

    # -------------------------
    # TRANSPORT RULES
    # -------------------------
    if transport_mode == "sea" and predicted_delay > 4:
        actions.append("Consider partial shift to air freight for urgent SKUs.")

    if transport_mode == "road" and route_risk:
        actions.append("Use alternate trucking route to avoid disruption.")

    if transport_mode == "air" and fuel_spike:
        actions.append("Review freight cost impact due to fuel price increase.")

    if transport_mode == "rail" and predicted_delay > 5:
        actions.append("Evaluate multimodal backup transport plan.")

    # -------------------------
    # EXTERNAL RISK RULES
    # -------------------------
    if weather_risk:
        actions.append("Weather disruption detected: add 1-2 day operational buffer.")

    if port_congestion:
        actions.append("Port congestion risk: reroute via alternate port if feasible.")

    if strike_risk:
        actions.append("Labor strike risk detected: secure backup carriers/vendors.")

    if customs_risk:
        actions.append("Customs delay likely: pre-clear documents immediately.")

    if fuel_spike:
        actions.append("Fuel volatility detected: review transportation budget.")

    if demand_spike:
        actions.append("Demand surge expected: increase replenishment quantities.")

    # -------------------------
    # RISK LEVEL RULES
    # -------------------------
    if risk_level == "high":
        actions.append("Create executive risk alert and mitigation review.")

    if risk_level == "medium":
        actions.append("Increase shipment monitoring frequency.")

    if risk_level == "low":
        actions.append("Maintain standard operating plan.")

    # -------------------------
    # COMBINED SMART RULES
    # -------------------------
    if risk_level == "high" and shipment_priority == "Same Day":
        actions.append("Activate critical shipment war-room response.")

    if predicted_delay > 5 and supplier_score < 50:
        actions.append("Switch immediate replenishment to backup supplier.")

    if predicted_delay > inventory_days_left and demand_spike:
        actions.append("High stockout risk: prioritize top-selling SKUs first.")

    if port_congestion and transport_mode == "sea":
        actions.append("Split shipment across multiple ports.")

    if strike_risk and supplier_score < 50:
        actions.append("Dual-source future procurement immediately.")

    # Remove duplicates
    actions = list(dict.fromkeys(actions))

    return actions