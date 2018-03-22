DOMAIN = {'tasks': {}}

MONGO_HOST = 'localhost'
MONGO_PORT = 27017

# Skip these if your db has no auth. But it really should.
#MONGO_USERNAME = '<your username>'
#MONGO_PASSWORD = '<your password>'

MONGO_DBNAME = 'catclassif'

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

MEDIA_PATH = 'C:\\Temp\\Rosdex-ML\\dev\\rest_category_classificator\\uploads'

task_schema = {
    'file': {'type': 'media'},
}

task = {
    # 'title' tag used in item links. Defaults to the resource title minus
    # the final, plural 's' (works fine in most cases but not for 'people')
    'item_title': 'task',


    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    # most global settings can be overridden at resource level
    'resource_methods': ['GET', 'POST', 'DELETE'],

    'schema': task_schema
}

DOMAIN = {
    'tasks': task,
}