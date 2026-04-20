import pandas as pd
from app.core.ml_model import Model
from app.core.data import Data
from app.services.final_predict import deliver_final_verdict, process_ai_risks
from pathlib import Path

if __name__=='__main__':
    BASE_DIR = Path(__file__).resolve().parent
    MODEL_DIR = BASE_DIR / "models"
    df=pd.read_csv('./data/Europe_supply_chain.csv')
    df=df[4:5]
    print(df['Order Country'])
    print(df['Customer Country'])
    
    clf_model=Model(str(MODEL_DIR / "model_delay_flag.pkl"), str(MODEL_DIR / "classifier_features.pkl"))
    reg_model=Model(str(MODEL_DIR / "model_delay_time.pkl"), str(MODEL_DIR / "regressor_features.pkl"))
    the_data=Data(dataframe=df)   
    the_dict=process_ai_risks(the_data)
    final_list=deliver_final_verdict(the_data, the_dict, clf_model, reg_model)
    for elem in final_list:
        print("")
        print(elem)