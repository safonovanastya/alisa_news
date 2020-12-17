# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import requests
from random import randint

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

import pprint
import time
from urlparse import urlparse

from requests import HTTPError

class YandexImages(object):
    def __init__(self):
        self.SESSION = requests.Session()
        #self.SESSION.headers.update(AUTH_HEADER)

        self.API_VERSION = 'v1'
        self.API_BASE_URL = 'https://dialogs.yandex.net/api/'
	self.API_URL = self.API_BASE_URL + '/' + self.API_VERSION + '/'
	self.skills = ''

    def set_auth_token(self, token):
        self.SESSION.headers.update(self.get_auth_header(token))

    def get_auth_header(self, token):
        return {
            'Authorization': 'OAuth %s' % token,
            "Content-Type": "application/json; charset=utf-8"
        }

    def log(self, error_text,response):
        log_file = open('YandexApi.log','a')
        log_file.write(error_text+'\n')#+response)
        log_file.close()

    def validate_api_response(self, response, required_key_name=None):
        content_type = response.headers['Content-Type']
        content = json.loads(response.text) if 'application/json' in content_type else None

        if response.status_code == 200:
            if required_key_name and required_key_name not in content:
                self.log('Unexpected API response. Missing required key: %s' % required_key_name, response=response)
                return None
        elif content and 'error_message' in content:
            self.log('Error API response. Error message: %s' % content['error_message'], response=response)
            return None
        elif content and 'message' in content:
            self.log('Error API response. Error message: %s' % content['message'], response=response)
            return None
        else:
            response.raise_for_status()

        return content

    ################################################
    # Проверить занятое место                      #
    #                                              #
    # Вернет массив                                #
    # - total - Сколько всего места осталось       #
    # - used - Занятое место                       #
    ################################################
    def checkOutPlace(self):
        result = self.SESSION.get(self.API_URL+'status')
        content = self.validate_api_response(result)
        if content != None:
            return content['images']['quota']
        return None

    ################################################
    # Загрузка изображения из интернета            #
    #                                              #
    # Вернет массив                                #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.               #
    ################################################
    def downloadImageUrl(self,url):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url=self.API_URL+path, data=json.dumps({"url":url}), headers=self.SESSION.headers)
        content = self.validate_api_response(result)
        if content != None:
            return content['image']
        return None


    ################################################
    # Загрузка изображения из файла                #
    #                                              #
    # Вернет массив                                #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.               #
    ################################################
    def downloadImageFile(self, img):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url = self.API_URL+path,files={'file':(img,open(img,'rb'))})
        content = self.validate_api_response(result)
        if content != None:
            return content['image']
        return None

    ################################################
    # Просмотр всех загруженных изображений        #
    #                                              #
    # Вернет массив из изображений                 #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.	           #
    ################################################
    def getLoadedImages(self):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.get(url = self.API_URL+path)
        content = self.validate_api_response(result)
        if content != None:
            return content['images']
        return None

    ################################################
    # Удаление выбранной картинки                  #
    #                                              #
    # В случае успеха вернет 'ok'	               #
    ################################################
    def deleteImage(self, img_id):
        path = 'skills/{skills_id}/images/{img_id}'.format(skills_id=self.skills,img_id = img_id)
        result = self.SESSION.delete(url=self.API_URL+path)
        content = self.validate_api_response(result)
        if content != None:
            return content['result']
        return None

    def deleteAllImage(self):
        success = 0
        fail = 0
        images = self.getLoadedImages()
        for image in images:
            image_id = image['id']
            if image_id:
                if self.deleteImage(image_id):
                    success+=1
                else:
                    fail += 1
            else:
                fail += 1

        return {'success':success,'fail':fail}


yandex = YandexImages()
yandex.set_auth_token(token = 'AgAAAAAFVw__AAT7o0bK8BXYR0elqUK5b9JzBUc')
yandex.skills = 'c7ab78ae-4fb6-4ea8-bed3-239fa4c140d4'


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
        number = randint(0, len(response.json()['articles']))
        title = response.json()['articles'][number]['title']
        link = response.json()['articles'][number]['url']
        image = response.json()['articles'][number]['urlToImage']
        ya_image_id = downloadImageUrl(image)

        res['response']['text'] = 'Вот такая есть новость из категории ' + req['request']['original_utterance'].lower() + ':\n' + title + '\n\n Для подробной информации нажми на картинку. \n\n\n Хочешь ещё новость? Выбери категорию!'
        res['response']['card'] = {'type' : 'BigImage', 'image_id' : ya_image_id, 'button' : {'text' : 'Подробнее', 'url' : link}}
        res['response']['buttons'] = get_suggests(user_id)
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
        for suggest in session['suggests'][:4]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    return suggests
