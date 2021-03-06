# -*- encoding: utf-8 -*-
import datetime as dt
import csv

from marshmallow import Schema, fields
from enum import Enum

from settings import BaseConfig
from classificator import CategoryClassificator

class JobStatus(Enum):
    CREATED = "CREATED"
    PERFORMING = "PERFORMING"
    DONE = "DONE"
    ERROR = "ERROR"

    def __str__(self):
        return str(self.value)

class Job():
    def __init__(self, uuid, input_fiename, ml_model_config):
        print('Create job with id = {0}'.format(uuid))
        print('Inpur filename = {0}'.format(input_fiename))

        self.uuid = uuid
        self.input_file = input_fiename
        self.output_file = ''
        self.status = JobStatus.CREATED
        self.created_at = dt.datetime.now()
        self.ml_model_config = ml_model_config


    def exec_job(self):
        # Step 0 - Set status Performing
        self.status = JobStatus.PERFORMING

        # Step 1 - Exctact product names
        products_names, product_ids = self.get_product_names()

        # Step 2 - Get ml model settings
        vectr_filename = self.ml_model_config.get_vect_filename()
        classif_filename = self.ml_model_config.get_classif_filename()

        print('Vect filename is {0}'.format(vectr_filename))
        print('Classif_filename is {0}'.format(classif_filename))

        # Step 3 - Create classificator
        ML_classificator = CategoryClassificator(vectr_filename, classif_filename)

        # Step 4 - Predict categories
        product_categories = self.predict_products_categories(ML_classificator, products_names)

        # Step 5 - merge product names and predicted categories
        # result_list = zip(products_names, product_categories)
        result_list = zip(product_ids, product_categories)

        # Step 6 - create result file
        self.output_file = self.generate_output_file(result_list)
        self.status = JobStatus.DONE


    def get_product_names(self):
        product_names = []
        product_ids = []
        filename = '\\'.join([BaseConfig.UPLOAD_DIR, self.input_file])

        with open(filename, newline='', encoding="utf8") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                # xantzhe
                product_ids.append(row[0])
                product_names.append(row[1])
                print('DEBUG name = {0}'.format(row[1]))

        return product_names, product_ids

    def predict_products_categories(self, classificator, product_names):
        product_categories = []

        for name in product_names:
            print('name is {0}'.format(name))
            category_id = classificator.predict_category_id(name)
            product_categories.append(category_id)

        return product_categories

    def generate_output_file(self, result_list):
        filename = '_'.join([self.uuid, 'output.csv'])

        with open('\\'.join([BaseConfig.RESULT_DIR, filename]),'wt', encoding='utf8') as file:
            for item in result_list:
                file.write('{0},{1}'.format(item[0], item[1][0]))
                file.write('\n')

        return filename

    def get_id(self):
        return self.uuid

    def get_result_filename(self):
        return self.output_file

    def check_status(self):
        result = False

        if self.status != JobStatus.DONE:
            result = True

        return result

    def __repr__(self):
        return '<Job(name={self.uuid!r})>'.format(self=self)

class JobSchema(Schema):
    uuid = fields.Str()
    #input_file = fields.Str()
    #output_file = fields.Str()
    status = fields.Str()
    created_at = fields.Date()
