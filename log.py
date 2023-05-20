import logging

log = logging.getLogger()
log.setLevel('INFO')

formatter = logging.Formatter(fmt='{asctime}  |  {levelname}  |  {lineno}  |  {message}', datefmt='d/%b/%Y %H:%M', style='{')
file_handler = logging.FileHandler(filename='log.log', mode='w', encoding='utf-8')
file_handler.setLevel('INFO')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)