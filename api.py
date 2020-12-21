# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import requests
from random import randint
from PIL import Image
from io import BytesIO

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    deleteAllImage()
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

def deleteImage(img_id):    

    url = 'https://dialogs.yandex.net/api/v1/skills/c7ab78ae-4fb6-4ea8-bed3-239fa4c140d4/images/' + img_id
    headers = {"Authorization": "OAuth AgAAAAAFVw__AAT7o0bK8BXYR0elqUK5b9JzBUc"}

    r = requests.delete(url, headers=headers)
    return 


def uploadImage(img):
    url = 'https://dialogs.yandex.net/api/v1/skills/c7ab78ae-4fb6-4ea8-bed3-239fa4c140d4/images'

    payload = {
        "url": img 
    }
    headers = {"Authorization": "OAuth AgAAAAAFVw__AAT7o0bK8BXYR0elqUK5b9JzBUc",
               "Content-Type": "application/json; charset=utf-8"}
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    data = json.loads(r.content)
    return data["image"]["id"]


def getLoadedImages():

    url = 'https://dialogs.yandex.net/api/v1/skills/c7ab78ae-4fb6-4ea8-bed3-239fa4c140d4/images'   
    headers = {"Authorization": "OAuth AgAAAAAFVw__AAT7o0bK8BXYR0elqUK5b9JzBUc"}
    r = requests.get(url, headers=headers)
    data = json.loads(r.content)

    return data['images']


def deleteAllImage():
    
    images = getLoadedImages()
    for image in images:
        image_id = image['id']
        deleteImage(image_id)

    return


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "спорт",
                "бизнес",
                "технологии",
                "наука",
                "здоровье",
            ]
        }
        res['response']['text'] = 'Привет! Выбирай одну из категорий (спорт, технологии, здоровье, наука, бизнес), а я тебе расскажу свежую новость!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'спорт',
        'бизнес',
        'технологии',
        'здоровье',
        'наука',
    ]:
        q = {'бизнес':'business', 'наука':'science', 'здоровье':'health', 'спорт':'sports', 'технологии':'technology'}
        url = "http://newsapi.org/v2/top-headlines?country=ru&category=" + q[req['request']['original_utterance'].lower()] + "&apiKey=c789ea7ca37b4600af9bd31acb9257b8"
        response = requests.get(url)
        if response:
            number = randint(0, len(response.json()['articles']))
            title = response.json()['articles'][number]['title']
            link = response.json()['articles'][number]['url']
            image = response.json()['articles'][number]['urlToImage']
            ya_image_id = uploadImage(image)

            res['response']['text'] = 'Вот такая есть новость из категории ' + req['request']['original_utterance'].lower() + ':\n' + title + '\n\n Для подробностей нажми на картинку. \n\n\n Хочешь ещё новость? Выбери категорию!'
            res['response']['card'] = {'type' : 'BigImage', 'image_id' : ya_image_id, 'button' : {'text' : 'Подробнее', 'url' : link}}
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = 'повторите, пожалуйста, запрос'
        return


    res['response']['text'] = 'Все говорят "%s", а ты лучше назови категорию!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id)

# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:5]
    ]
    return suggests