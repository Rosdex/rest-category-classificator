import numpy as np
import pandas as pd
import os

from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from sklearn.utils import shuffle

#wrapper for Tomita parser
from tomita_parser import TomitaParser

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

ML_MODELS_DIR = 'ml_models'

TOMITA_BIN_PATH = '\\'.join([BASE_PATH, 'tomita', 'tomitaparser.exe'])
TOMITA_CONFIG_PATH = '\\'.join([BASE_PATH, 'tomita', 'config', 'config.proto'])

class CategoryClassificator:

    def __init__(self, vectorizator_name, classififcator_name):
        # prepare Tomita Parser
        self.tomita = TomitaParser(TOMITA_BIN_PATH, TOMITA_CONFIG_PATH, debug=False)

        # load vectorizator
        vectorizator_path = '/'.join([ML_MODELS_DIR, vectorizator_name])
        self.vectorizer = joblib.load(vectorizator_path)

        # load svm classification model
        svm_path = '/'.join([ML_MODELS_DIR, classififcator_name])
        self.clf = joblib.load(svm_path)

    def predict_category_id(self, product_name):
        # collect product_name facts
        facts, leads = self.tomita.run(product_name)

        # first fact is clear product_name
        clear_name = self.fact_to_string(facts[0])

        # transform name to vector
        vector = self.vectorizer.transform([clear_name])
        np_vector = self.create_np_array_from_vector(vector)

        # get predicted value
        predicted_value = self.clf.predict(np_vector)

        return predicted_value


    def fact_to_string(self, fact):
        result_str = "{0} {1} ".format(fact['fact'], fact['adjForName'])
        result_str = result_str.lower().strip()
        return result_str

    def create_np_array_from_vector(self, vector):
        vec_arr = vector.toarray()
        vec_list = []
    
        for i in range(0, vector.shape[1]):
            vec_list.append(vec_arr[0,i])
        
        return np.array(vec_list)