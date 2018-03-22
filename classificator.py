import numpy as np
import pandas as pd

from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from sklearn.utils import shuffle

#wrapper for Tomita parser
from tomita_parser import TomitaParser

class CategoryClassificator:

    def __init__(self):
        # prepare Tomita Parser
        self.tomita = TomitaParser('C:\\Temp\\Rosdex-ML\\dev\\rest_category_classificator\\tomita\\tomitaparser.exe', 'C:\\Temp\\Rosdex-ML\\dev\\rest_category_classificator\\tomita\\config\\config.proto', debug=False)

        # load vectorizator
        vectorizator_path = 'models\\vectorizator.sav'
        self.vectorizer = joblib.load(vectorizator_path)

        # load svm classification model
        svm_path = 'models\\svm.sav'
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