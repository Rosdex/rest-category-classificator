import os
import uuid
import json

from job import JobStatus, Job, JobSchema
from flask import Flask, request, send_file,  jsonify

from classificator_settings import ModelConfig, ModelConfigSchema

# Constants
# =========
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = 'uploads'
ML_MODEL_DIR = 'ml_models'
RESULT_DIR = 'result_files'

# Extensions initialization
# =========================
app = Flask(__name__)


jobs = []
available_ml_models = []
active_model_uuid = []

# Statrup fuctions
# ================
@app.before_first_request
def add_default_ml_model():
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
    input_filenames = upload_files(UPLOAD_DIR, job_uuid)
    print('File was uploaded, name is {0}'.format(input_filenames[0]))

    # Step 2 - Get current ml model config
    ml_config = get_item_by_id(available_ml_models, active_model_uuid[0])

    print(active_model_uuid[0])
    print(ml_config)

    # Step 3 - Create job
    job = Job(job_uuid, input_filenames[0], ml_config)

    # Step 4 - Save data about Job
    jobs.append(job)

    # Step 5 - Prepare response 
    schema = JobSchema(many=False)
    job_dump = schema.dump(job)

    return jsonify(job_dump.data)

@app.route('/jobs/<uuid>/perform', methods = ['POST'])
def perform_job(uuid):
    job = get_item_by_id(jobs, uuid)

    if job != None:
        job.exec_job()
        return "", 204
    else:
        return "", 404

@app.route('/jobs/<uuid>', methods = ['GET'])
def get_job(uuid):
    job = get_item_by_id(jobs, uuid)

    if job != None:
        schema = JobSchema(many=False)
        job_dump = schema.dump(job)
        return jsonify(job_dump.data)
    else:
        return "", 404

@app.route('/jobs/<uuid>/result', methods = ['GET'])
def get_job_result(uuid):
    job = get_item_by_id(jobs, uuid)

    if job != None:
        result_filename = job.get_result_filename()
        if result_filename != '':
            return send_file('/'.join([APP_ROOT, RESULT_DIR, result_filename]), attachment_filename=result_filename)
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

    if ml_model != None:
        schema = ModelConfigSchema(many=False)
        ml_model_dump = schema.dump(ml_model)
        return jsonify(ml_model_dump.data)
    else:
        return "", 404

@app.route('/ml-models', methods=['POST'])
def add_ml_model():
    # Step 0 - Generate UUID for new Job
    ml_model_uuid = uuid.uuid1().hex

    # Step 1 - upload file
    input_filenames = upload_files(ML_MODEL_DIR, ml_model_uuid)
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

    # Step 6 - Prepare response 
    schema = ModelConfigSchema(many=False)
    ml_model_dump = schema.dump(ml_model)

    return jsonify(ml_model_dump.data)

# Helper functions
# ================
def get_item_by_id(collection, uuid):
    target_item = None

    for item in collection:
        if item.get_id() == uuid:
            target_item = item
            break

    return target_item

def upload_files(dir_prefix, name_prefix):
    target = os.path.join(APP_ROOT, dir_prefix)
    filenames = []

    for upload in request.files.getlist("file"):
        filename = '_'.join([name_prefix, upload.filename])
        upload.save('/'.join([target, filename]))
        filenames.append(filename)

    return filenames
