# -*- encoding: utf-8 -*-
import os
import uuid
import json

from flask import Flask, request, send_file,  jsonify
from threading import Thread

from settings import BaseConfig
from job import JobStatus, Job, JobSchema
from classificator_config import ModelConfig, ModelConfigSchema

# Extensions initialization
# =========================
app = Flask(__name__)

# Data layer - Collections
# ========================
jobs = []
available_ml_models = []
active_model_uuid = []

# Statrup fuctions
# ================
@app.before_first_request
def add_default_ml_model():
    # Setup default ml model
    active_model_uuid.append(uuid.uuid1().hex)

    ml_model = ModelConfig(
        active_model_uuid[0], 
        'vectorizator.sav', 
        'svm.sav'
    )

    available_ml_models.append(ml_model)

# Routes - Job domain
# ===================
@app.route("/")
def defalut_route():
    print(active_model_uuid[0])
    return 'Welcome to catecory prediction service'

@app.route('/jobs')
def get_jobs():
    schema = JobSchema(many=True)
    jobs_dump = schema.dump(jobs)
    return jsonify(jobs_dump.data)

@app.route('/jobs', methods=['POST'])
def create_job():
    # Step 0 - Generate UUID for new Job
    job_uuid = uuid.uuid1().hex

    # Step 1 - upload file
    input_filenames = upload_files(BaseConfig.UPLOAD_DIR, job_uuid)
    print('File was uploaded, name is {0}'.format(input_filenames[0]))

    # Step 2 - Get current ml model config
    ml_config = get_item_by_id(available_ml_models, active_model_uuid[0])

    print(active_model_uuid[0])
    print(ml_config)

    # Step 3 - Create job
    job = Job(job_uuid, input_filenames[0], ml_config)

    # Step 4 - Save data about Job
    jobs.append(job)

    # Step 5 - Send response 
    return job_to_json(job)

@app.route('/jobs/<uuid>/perform', methods = ['POST'])
def perform_job(uuid):
    job = get_item_by_id(jobs, uuid)

    if job:
        thr = Thread(target=perform_async_job, args=[app, job])
        thr.start()
        return job_to_json(job)
    else:
        return "", 404

@app.route('/jobs/<uuid>', methods = ['GET'])
def get_job(uuid):
    job = get_item_by_id(jobs, uuid)

    if job:
        return job_to_json(job)
    else:
        return "", 404

@app.route('/jobs/<uuid>/result', methods = ['GET'])
def get_job_result(uuid):
    job = get_item_by_id(jobs, uuid)

    if job:
        result_filename = job.get_result_filename()
        if result_filename != '':
            return send_file('/'.join([BaseConfig.APP_ROOT, BaseConfig.RESULT_DIR, result_filename]), attachment_filename=result_filename)
    else:
        return "", 404

# Routes - Classificator config domain
# ====================================
@app.route('/ml-models')
def get_ml_models():
    schema = ModelConfigSchema(many=True)
    models_dump = schema.dump(available_ml_models)
    return jsonify(models_dump.data)

@app.route('/ml-models/<uuid>', methods = ['GET'])
def get_ml_model(uuid):
    ml_model = get_item_by_id(available_ml_models, uuid)

    if ml_model:
        return model_to_json(ml_model)
    else:
        return "", 404

@app.route('/ml-models', methods=['POST'])
def add_ml_model():
    # Step 0 - Generate UUID for new Job
    ml_model_uuid = uuid.uuid1().hex

    # Step 1 - upload file
    input_filenames = upload_files(BaseConfig.ML_MODELS_DIR, ml_model_uuid)
    print(input_filenames)

    # Step 2 find vectorizator file
    vectorizator_name = '_'.join([ml_model_uuid, 'vectorizator.sav'])
    classificator_name = '_'.join([ml_model_uuid, 'svm.sav'])

    # Step 3 - Create ml model
    ml_model = ModelConfig(
        ml_model_uuid, 
        vectorizator_name, 
        classificator_name
    )

    # Step 4 - Save ml model
    available_ml_models.append(ml_model)

    # Step 5 - Activate new model
    active_model_uuid.clear()
    active_model_uuid.append(ml_model_uuid)

    # Step 6 - Send response
    return model_to_json(ml_model) 

# Helper functions
# ================
def get_item_by_id(collection, uuid):
    for item in collection:
        if item.get_id() == uuid:
            return item
    return None

def upload_files(dir_prefix, name_prefix):
    target = os.path.join(BaseConfig.APP_ROOT, dir_prefix)
    filenames = []

    for upload in request.files.getlist("file"):
        filename = '_'.join([name_prefix, upload.filename])
        upload.save('/'.join([target, filename]))
        filenames.append(filename)

    return filenames

def perform_async_job(app, job):
    with app.app_context():
        print('----- Start async Job -----')
        job.exec_job()
        print('----- End async Job -----')

def job_to_json(job):
    schema = JobSchema(many=False)
    job_dump = schema.dump(job)
    return jsonify(job_dump.data)

def model_to_json(ml_model):
    schema = ModelConfigSchema(many=False)
    ml_model_dump = schema.dump(ml_model)
    return jsonify(ml_model_dump.data)