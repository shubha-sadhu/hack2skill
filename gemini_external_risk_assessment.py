from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import json
import re
import time

class AI_Model(object):
    def __init__(self, model_name, api_key):
        self.model_name=model_name
        load_dotenv()
        self.API_KEY = os.getenv(api_key)
        if not self.API_KEY:
            raise ValueError('API key not found in env file')
        self.client = genai.Client(api_key=self.API_KEY)
    def get_response_text(self, the_prompt, google_search=True):
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=the_prompt,
            
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.25
            ) if google_search else None
        )
        return response.text
    
    def extract_json(self,text):
            try:
                return json.loads(text)
            except:
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
                raise ValueError("No valid JSON found")

    def get_json_response(self, the_prompt, google_search=True, tries=3):
        for i in range(tries):
            try:
                the_response=self.get_response_text(the_prompt, google_search)
                if the_response==None or the_response==[]:
                    #print(the_response)
                    return None
                else:
                    clean_response = self.extract_json(the_response)
                    return clean_response
            except Exception as e:
                time.sleep(2 ** i)
                if i==(tries-1):
                    raise ValueError("Failed after retries") from e
        

if __name__=='__main__':
    gemini_2=AI_Model('gemini-2.5-flash-lite', 'GEMINI_API_KEY')
    json_reponse=gemini_2.get_json_response("""
        Search and analyze news that may cause supply chain disruptions on road/air/sea.
        Instructions:
        - If the disruption is local i.e. causes problem for city/a few cities, replace 
          country list with city list
        - Return countries/cities affected as a list of ISO codes
        - Return disruption timeline in MM/DD/YYYY format only(don't give a end date if not sure about it)
        - Identify ALL affected transport modes (sea, air, road)
        - Consider both DIRECT impacts (e.g., port closures) and INDIRECT impacts (e.g., airspace restrictions, rerouting, fuel shortages)
        - Do NOT omit any mode if reasonably affected
        - If uncertain, include the mode with lower confidence rather than excluding it
        - Give a source url to an article containing details about the news
        Return ONLY JSON:
        [
        {
            "country/ city": "",
            "risk_type": "",
            "severity": "low/medium/high",
            "Expected disruption timeline": ""
            "affected_modes": [{"air": "confidence(0-1)", 
                                "road": "confidence(0-1)"}, 
                                "sea": "confidence(0-1)", 
                                "rail": "confidence(0-1)"}
                              ]
            "URL":""
        }
        ]
    """,
    )
    
    print(json_reponse)
    print("")
    for object in json_reponse:
        print(object)
        
