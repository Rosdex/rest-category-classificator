from classificator import CategoryClassificator

if __name__ == "__main__":
    ML_classificator = CategoryClassificator()

    product_name = 'Фонарь налобный Petzl Tikka 2'

    category_dict = {114636: 'Дрели', 1: 'Шины', 2: 'Диски', 1630: 'Дальномеры', 114637: 'Фонари', 114838: 'Струбцина и зажимы', 
        114856: 'цепи для инструментов', 114862: 'Бензопилы', 114903: 'Корды для триммеров', 114906: 'Газонокосилки',
        115047: 'Буры', 115117: 'Сверла'}

    predicted_value = ML_classificator.predict_category_id(product_name)

    print('Target category is {}'.format(category_dict[predicted_value[0]]))
