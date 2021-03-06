import logging
from urlparse import urlparse

from flask import Flask
from flask.ext.assets import Environment, Bundle
from kombu import Exchange, Queue
from celery import Celery
from pymongo import MongoClient

from newsclipse import default_settings

logging.basicConfig(level=logging.DEBUG)

# specific loggers
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('pyelasticsearch').setLevel(logging.WARNING)


app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('NEWSCLIPSE_SETTINGS', silent=True)

assets = Environment(app)
if app.config.get('PRODUCTION'):
    assets.auto_build = False

mongo = MongoClient(app.config.get('MONGO_URL'))
db = mongo[urlparse(app.config.get('MONGO_URL')).path[1:]]

calais_key = app.config.get('CALAIS_KEY')
if calais_key is None:
    raise SystemError('Please set $CALAIS_KEY in the config or environment!')

queue_name = 'newsclipse_q'
app.config['CELERY_DEFAULT_QUEUE'] = queue_name
app.config['CELERY_QUEUES'] = (
    Queue(queue_name, Exchange(queue_name), routing_key=queue_name),
)

celery = Celery('newsclipse', broker=app.config['CELERY_BROKER_URL'])
celery.config_from_object(app.config)


assets.register('css', Bundle('style/app.less',
                              filters='less',
                              output='assets/style.css'))

assets.register('js', Bundle("vendor/angular/angular.js",
                             "vendor/angular-route/angular-route.js",
                             "vendor/angular-animate/angular-animate.js",
                             "vendor/angular-contenteditable/angular-contenteditable.js",
                             "vendor/angular-truncate/src/truncate.js",
                             "vendor/angular-bootstrap/ui-bootstrap.js",
                             "vendor/angular-bootstrap/ui-bootstrap-tpls.js",
                             "vendor/angular-loading-bar/build/loading-bar.js",
                             "vendor/angular-loading-bar/build/loading-bar.js",
                             "js/app.js",
                             filters='uglifyjs',
                             output='assets/app.js'))
