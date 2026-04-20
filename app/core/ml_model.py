import joblib

class Model(object):
    def __init__(self, model_pkl_file, features_pkl_file):
        self.model=joblib.load(model_pkl_file)
        self.features=joblib.load(features_pkl_file)

    def get_prediction(self, df):
        X=df[self.features]
        return self.model.predict(X)[0]
    
    def get_probability(self, df):
        X=df[self.features]
        return self.model.predict_proba(X)[0][1]
