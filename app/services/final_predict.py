from app.core.ai_model import AI_Model
from app.core.data import Data
from app.core.ml_model import Model
from app.services.generate_recs import generate_recommendations
from collections import defaultdict
import pandas as pd


def ml_predict(data: Data, clf_model, reg_model):
    clf_df = data.prepare_for_model(clf_model, ['Order Status', 'Shipping Mode'])
    delay_flag = clf_model.get_prediction(clf_df)
    delay_prob = clf_model.get_probability(clf_df)
    delay_days=0

    if(delay_flag):
        reg_df = data.prepare_for_model(reg_model)
        delay_days = reg_model.get_prediction(reg_df)

    return {
        "will_delay": int(delay_flag),
        "delay_probability": float(delay_prob),
        "delay_days": float(delay_days),
        "expected_delay": float(delay_prob * delay_days)
    }

def compute_route_risk(disruptions):
    severity_map = {"low": 0.2, "medium": 0.5, "high": 0.9}
    
    scores = []
    for d in disruptions:
        sev = severity_map.get(d.get('severity', 'low'), 0.2)
        
        mode_scores = []
        # print(d.get('affected_modes'))
        # print(type(d.get('affected_modes')))
        for score in d.get('affected_modes', {}).values():
            try:
                mode_scores.append(float(score))
            except:
                continue
        
        mode_score = max(mode_scores) if mode_scores else 0.5
        
        scores.append(sev * mode_score)
    
    return max(scores) if scores else 0


def deliver_final_verdict(data: Data, disruption_dict:dict, clf_model, reg_model):
    df=data.get_dataframe()
    response_list=[]
    
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        data_obj = Data.from_dict(row_dict)

        response=ml_predict(data_obj, clf_model, reg_model)

        c1=row_dict.get('Customer Country')
        c2=row_dict.get('Order Country')
        route=frozenset([c1, c2])
        if not c1 or not c2:
            response['external_risk'] = None
        elif route in disruption_dict:
            response['external_risk'] = compute_route_risk(disruption_dict[route])
            # response['External Disruption Chance']=[d['severity'] for d in disruption_dict[route]]
            # response['Context']=[disruption_dict[route]]
        else:
            response['external_risk'] = 0
            # response['External Disruption Chance']='low'

        if(response["external_risk"])==None:
            response["external_risk"]=0.2
                        
        final_score = (
            0.6 * response["delay_probability"] +
            0.2 * min(response["delay_days"]/10, 1) +
            0.2 * response["external_risk"]
        )
        response["final_risk_score"] = final_score
        risk_types = disruption_dict.get(route, [{}])[0].get("risk_type") or []
        actions= generate_recommendations(
            predicted_delay=float(response["expected_delay"]),
            risk_level=str(risk_types),
            shipment_priority=str(row_dict.get("Shipping Mode")),
            transport_mode=str(row_dict.get("Transport_mode")),
            inventory_days_left=int(row_dict.get("Inventory_days") or 5),
            supplier_score=float(row_dict.get("Supplier_score") or 0.5),

            port_congestion=("port_congestion" in risk_types),
            weather_risk=("weather_risk" in risk_types),
            strike_risk=("strike_risk" in risk_types),
            fuel_spike=("fuel_spike" in risk_types),
            customs_risk=("customs_risk" in risk_types),
            demand_spike=("demand_spike" in risk_types),
            route_risk=("route_risk" in risk_types)
        )
        response["actions"]=actions
        
        response_list.append(response)

        response_list.append(response)

    return response_list


def process_ai_risks(data: Data):
    gemini_2=AI_Model('gemini-2.5-flash', 'GEMINI_API_KEY')
    df=data.get_dataframe()

    routes=set()
    for _, row in df.iterrows(): 
        c1=row.get('Customer Country')
        c2=row.get('Order Country')
        if not c1 or not c2:
            continue  # skip invalid rows
        routes.add(frozenset([c1,c2]))

    disruption_dict=defaultdict(list)
    for route in routes:
        route_list=sorted(list(route))

        if len(route_list) < 2:
            continue #skip invaid/same routes
        
        the_response=gemini_2.get_json_response(f"""
        Search and analyze news that may cause supply chain disruptions on road/air/sea for 
        shipments between {route_list[0]} and {route_list[1]}.
        Instructions:
        - If the disruption causes problem for a city only, mention that city in "City" as a list element
        - If the disruption causes problem for a country on a whole mention that country it in "Country" as
          a list element
        - Return countries/cities affected as a list of ISO codes
        - Risk type should be chosen from the following options: 
            =>"port_congestion", "weather_risk", "strike_risk", "fuel_spike", "customs_risk", "route_risk"
            =>Include the options as a list so that two or more options may be included 
        - Return disruption timeline in MM/DD/YYYY format only(don't give a end date if not sure about it)
        - Identify ALL affected transport modes (sea, air, road)
        - Consider both DIRECT impacts (e.g., port closures) and INDIRECT impacts (e.g., airspace restrictions, rerouting, fuel shortages)
        - Do NOT omit any mode if reasonably affected
        - 'affected modes' should return its information as a dictionary with "air", "road", "rail", "sea" as keys
        - If uncertain, include the mode with lower confidence rather than excluding it
        - Give a source url to an article containing details about the news
        Return ONLY JSON:
        [
        {{
            "City": [],
            "Countries": [],
            "risk_type": [],
            "severity": "low/medium/high",
            "Expected disruption timeline": "",
            "affected_modes": {{"air": "confidence(0-1)", 
                                "road": "confidence(0-1)", 
                                "sea": "confidence(0-1)", 
                                "rail": "confidence(0-1)"}}
                              ,
            "URL":""
        }}
        ]
    """)
        if the_response:
            for the_dict in the_response:    
                disruption_dict[route].append(the_dict)

    #print(the_response)
    return disruption_dict

