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