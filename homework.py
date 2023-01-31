import logging
import logging.config
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ENDPOINT = os.getenv('ENDPOINT')
RETRY_PERIOD = 600
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logger = logging.getLogger(__name__)


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """проверяет доступность переменных окружения."""
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    )
    if not all(tokens):
        logging.critical('Нет переменной окружения')
    return all(tokens)


def send_message(bot, message):
    """отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Сообщение {message} отправлено')
    except Exception as error:
        logging.error(f'Ошибка отправки {error}')


def get_api_answer(timestamp) -> dict:
    """делает запрос к единственному эндпоинту API."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        logging.debug(f'Ошибка {error}', exc_info=True)
    if response.status_code != HTTPStatus.OK:
        raise Exception.ResponseStatusError(
            f'нет доступа к API. {response.status_code}',
            exc_info=True
        )
    try:
        response.json()
    except Exception as error:
        logging.error(f'ответ не в json, {error}')
    return response.json()


def check_response(response):
    """проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Запрос должен быть словарем!')
    if 'homeworks' not in response:
        raise ValueError('Нет инфы о дз')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Дз должен быть списком!')
    return response['homeworks']


def parse_status(homework):
    """извлекает из информации о конкретной домашней работе."""
    try:
        status = homework['status']
    except Exception:
        logging.error('Ошибка')
        raise KeyError('Ошибка')
    try:
        homework_name = homework['homework_name']
    except Exception:
        logging.error('нет ключа')
        raise KeyError('нет ключа')
    if homework['status'] in homework:
        status = homework['status']
    if status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Токены отсутствуют!')
        sys.exit('Токены отсутствуют!')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - RETRY_PERIOD
    status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if len(homework) > 0:
                message = parse_status(homework[0])
                send_message(bot, message)
                timestamp = response['current_date']
                time.sleep(RETRY_PERIOD)
        except Exception as error:
            if error != status:
                message = f'Сбой в работе программы: {error}'
                logger.error(message, exc_info=True)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
