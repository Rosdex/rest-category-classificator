# -*- encoding: utf-8 -*-
import os
import uuid
import json

from flask import Flask, request, send_file,  jsonify
from flask_restplus import Resource, Api
from werkzeug.datastructures import FileStorage
from threading import Thread

from settings import BaseConfig
from job import JobStatus, Job, JobSchema
from classificator_config import ModelConfig, ModelConfigSchema

# Extensions initialization
# =========================
app = Flask(__name__)
api = Api(app, version='1.0', title='Name classificator API',
    description='This service using for product by name classification',
)

ns_jobs = api.namespace('jobs', description='Jobs for classification by name')
ns_ml_models = api.namespace('ml-models', description='Domain for controlling ML models')

upload_parser = api.parser()
upload_parser.add_argument('file', location=BaseConfig.UPLOAD_DIR,
                           type=FileStorage, required=True)

upload_parser2 = api.parser()
upload_parser2.add_argument('file', location=BaseConfig.ML_MODELS_DIR,
                           type=FileStorage, required=True)

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
    active_model_uuid.append(str(uuid.uuid1()))

    ml_model = ModelConfig(
        active_model_uuid[0], 
        'vectorizator.sav', 
        'svm.sav'
    )

    available_ml_models.append(ml_model)

# Routes - Job domain
# ===================
@ns_jobs.route('/')
class JobList(Resource):
    # Shows a list of all jobs, and lets you POST to add new jobs
    def get(self):
        # List all jobs
        schema = JobSchema(many=True)
        jobs_dump = schema.dump(jobs)
        return jsonify(jobs_dump.data)

    @ns_jobs.expect(upload_parser)
    def post(self):
        # Create a new job
        # Step 0 - Generate UUID for new Job
        job_uuid = str(uuid.uuid1())

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

        # WARNING bad solution
        thr = Thread(target=perform_async_job, args=[app, job])
        thr.start()

        # Step 5 - Send response 
        return job_to_json(job)

@ns_jobs.route('/<uuid>')
@ns_jobs.param('uuid', 'The job identifier')
class JobView(Resource):
    # Show a single job 
    def get(self, uuid):
        job = get_item_by_id(jobs, uuid)
        if job:
            return job_to_json(job)
        else:
            return "Job not found", 404

@ns_jobs.route('/<uuid>/perform')
@ns_jobs.param('uuid', 'The job identifier')
class JobPerformaer(Resource):
    # Perform specific Job
    def post(self, uuid):
        job = get_item_by_id(jobs, uuid)
        if job:
            thr = Thread(target=perform_async_job, args=[app, job])
            thr.start()
            return job_to_json(job)
        else:
            return "Job not found", 404

@ns_jobs.route('/<uuid>/result')
@ns_jobs.param('uuid', 'The job identifier')
class JobResultProvider(Resource):
    def get(self, uuid):
        job = get_item_by_id(jobs, uuid)
        if job:
            result_filename = job.get_result_filename()
            if result_filename != '':
                return send_file('/'.join([BaseConfig.APP_ROOT, BaseConfig.RESULT_DIR, result_filename]), attachment_filename=result_filename)
        else:
            return "", 404

# Routes - Classificator config domain
# ====================================
@ns_ml_models.route('/')
class ModelList(Resource):
    # Shows a list of all ml models, and lets you POST to add new ml models
    def get(self):
        # List all ml models
        schema = ModelConfigSchema(many=True)
        models_dump = schema.dump(available_ml_models)
        return jsonify(models_dump.data)

    @ns_ml_models.expect(upload_parser2)
    def post(self):
        # Add a new ML model
        # Step 0 - Generate UUID for new Job
        ml_model_uuid = str(uuid.uuid1())

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

@ns_ml_models.route('/<uuid>')
@ns_ml_models.param('uuid', 'The ML model identifier')
class ModelView(Resource):
    # Show a single job 
    def get(self, uuid):
        ml_model = get_item_by_id(available_ml_models, uuid)
        if ml_model:
            return model_to_json(ml_model)
        else:
            return "", 404

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