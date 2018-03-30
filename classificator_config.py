# -*- encoding: utf-8 -*-
from marshmallow import Schema, fields

class ModelConfig():
    def __init__(self, uuid, vectoriz, classif):
        self.uuid = uuid
        self.vectorizator_file = vectoriz
        self.model_file = classif

    def get_id(self):
        return self.uuid

    def get_vect_filename(self):
        return self.vectorizator_file

    def get_classif_filename(self):
        return self.model_file

class ModelConfigSchema(Schema):
    uuid = fields.Str()
    vectorizator_file = fields.Str()
    model_file = fields.Str()