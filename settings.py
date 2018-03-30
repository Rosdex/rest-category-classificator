# -*- encoding: utf-8 -*-
import os

# Constants
# =========
class BaseConfig(object):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

    UPLOAD_DIR = 'uploads'
    ML_MODELS_DIR = 'ml_models'
    RESULT_DIR = 'result_files'

    TOMITA_BIN_PATH = '\\'.join([APP_ROOT, 'tomita', 'tomitaparser.exe'])
    TOMITA_CONFIG_PATH = '\\'.join([APP_ROOT, 'tomita', 'config', 'config.proto'])