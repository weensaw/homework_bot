import logging

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
logging.debug('удачная отправка любого сообщения')
logging.debug('отсутствует в ответе новый статус')
logging.info('Сообщение отправлено')
logging.warning('Большая нагрузка!')
logging.error('Бот не смог отправить сообщение')
logging.error('недоступность эндпоинта')
logging.error('сбои при запросе к эндпоинту')
logging.error('отсутствие ожидаемых ключей в ответе API')
logging.error('неожиданный статус домашней работы')
logging.critical('Отсутствует обязательная переменная окружения')
