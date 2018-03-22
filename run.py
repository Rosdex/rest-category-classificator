import json
from eve import Eve
from eve_fsmediastorage import FileSystemMediaStorage
from classificator import CategoryClassificator
from flask_pymongo import PyMongo
#------------------------------------------------------------------

def post_task_get_callback(request, payload):
    print('A GET on "task" was just performed!')

def post_task_post_callback(request, response):
    print('A POST on "task" was just performed!')
    print(request.files)
    print('------------')

    data = response.get_data()
    data = data.decode("utf-8")
    print(data)
    data = json.loads(data)

    task_id = data['_id']
    print('Task id = {0}'.format(task_id))

    #task_files = mongo.db.tasks_files
    #task_file = task_files.find_one({'_id' : task_id})

    #if task_file:
    #    output = 'Filename is {0}'.format()
    #else:
    #    output = "No such name"
    #print(output)




app = Eve(media=FileSystemMediaStorage)

mongoObj = PyMongo(app)

app.on_post_GET_tasks += post_task_get_callback
app.on_post_POST_tasks += post_task_post_callback


@app.route('/hello')
def hello_world():
    ML_classificator = CategoryClassificator()

    product_name = 'Фонарь налобный Petzl Tikka 2'

    category_dict = {114636: 'Дрели', 1: 'Шины', 2: 'Диски', 1630: 'Дальномеры', 114637: 'Фонари', 114838: 'Струбцина и зажимы', 
        114856: 'цепи для инструментов', 114862: 'Бензопилы', 114903: 'Корды для триммеров', 114906: 'Газонокосилки',
        115047: 'Буры', 115117: 'Сверла'}

    predicted_value = ML_classificator.predict_category_id(product_name)

    return category_dict[predicted_value[0]]

@app.route('/hello/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

if __name__ == '__main__':
    app.run()