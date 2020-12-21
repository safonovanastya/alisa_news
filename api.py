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

# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        res['response']['text'] = 'Привет! Выбирай одну из категорий (спорт, технологии, здоровье, наука, бизнес), а я тебе расскажу свежую новость! Если новость заинтересует -- жми "подробнее"ю'
        res['response']['buttons'] = [{title: "спорт"}, {title: "здоровье"}, {title: "технологии"}, {title: "бизнес"}, {title: "наука"}]
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
        title = response.json()['articles'][number]['description']
        link = response.json()['articles'][number]['url']

        res['response']['text'] = 'Вот такая есть новость из категории ' + req['request']['original_utterance'].lower() + ':\n\n' + title + '\n\n\n Хочешь ещё новость? Выбери категорию!'
        res['response']['buttons'] = [{"title": "Подробнее", "url": link}]
        return

    res['response']['text'] = 'Все говорят "%s", а ты лучше назови категорию!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = [{title: "спорт"}, {title: "здоровье"}, {title: "технологии"}, {title: "бизнес"}, {title: "наука"}]
