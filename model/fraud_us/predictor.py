import os
import numpy as np
import hsfs
import joblib

class Predict(object):

    def __init__(self):
        """ Initializes the serving state, reads a trained model"""        
        # get feature store handle
        fs_conn = hsfs.connection()
        self.fs = fs_conn.get_feature_store()
        
        # get feature view
        self.fv = self.fs.get_feature_view("fraud_model_us", 1)
        
        # initialise serving
        self.fv.init_serving(1)

        # load the trained model
        self.model = joblib.load(os.environ["ARTIFACT_FILES_PATH"] + "/model.pkl")
        print("Initialization Complete")

    def predict(self, inputs):
        """ Serves a prediction request using a trained model"""
        feature_vector = self.fv.get_feature_vector({"cc_num": inputs[0]})
        return self.model.predict(np.asarray(feature_vector).reshape(1, -1)).tolist() 