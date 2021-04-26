from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# создаем словарь, в котором ключ — название музея,
# а значение — массив, где перечислены id картинок,
# которые мы записали в прошлом пункте.

data = {
    'эрмитаж': ['1030494/4ea425cfa71df2f7016b'],
    'мсиид': ['1521359/d71af8957027a44204da'],
    'музей имени радищева': ['1521359/33ec1aeb4c893be75883'],
    'третьяковская галерея': ['937455/0ecf3cdf35b92c63f71a']
}
buttons = {
    'эрмитаж': 'http://haleinee.herokuapp.com/ermitag',
    'мсиид': 'http://haleinee.herokuapp.com/msiid',
    'музей имени радищева': 'http://haleinee.herokuapp.com/sarat',
    'третьяковская галерея': 'http://haleinee.herokuapp.com/tret'
           }
# создаем словарь, где для каждого пользователя
# мы будем хранить его имя
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        # создаем словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None
        }
        return

    # если пользователь не новый, то попадаем сюда.
    # если поле имени пустое, то это говорит о том,
    # что пользователь еще не представился.
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя.
        # И спрашиваем какой музей он хочет увидеть.
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' \
                          + first_name.title() \
                          + '. Я - Алиса. Какой музей хочешь увидеть?'
            # получаем варианты buttons из ключей нашего словаря data
            res['response']['buttons'] = [
                {
                    'title': museum.title(),
                    'hide': True
                } for museum in data
            ]
    # если мы знакомы с пользователем и он нам что-то написал,
    # то это говорит о том, что он уже говорит о музее,
    # что хочет увидеть.
    else:
        # ищем музей в сообщение от пользователя
        museum = get_museum(req)
        # если этот музей среди известных нам,
        # то показываем его (выбираем одну из двух картинок случайно)
        if museum in data:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот музей я знаю.'
            res['response']['card']['image_id'] = random.choice(data[museum])
            res['response']['buttons'] = [
                {
                    'title': museum,
                    "url": buttons[museum],
                    'hide': True
                }]
            res['response']['text'] = 'Я угадала!'
        # если не нашел, то отвечает пользователю
        # 'Первый раз слышу об этом музее.'
        else:
            res['response']['text'] = \
                'Первый раз слышу об этом музее. Попробуй еще разок!'


def get_museum(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['tokens']:
        if entity.lower() in data:
            return entity.lower()
        else:
            return None


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
