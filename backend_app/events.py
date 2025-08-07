import json

# Flask
from flask import session
from flask_socketio import emit, send

# Kafka
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

from .schemas_objects import GPSData, dict_to_gpsdata
from .schema import gps_data_schema_str
from .config import config


from . import socketio

consumer = None

def set_consumer_config():
    config['group.id'] = 'gps_group'
    config['auto.offset.reset'] = 'earliest'


def send_coordinate_data():
    """
    Will continously send data to the client in the background
    """
    global consumer
    json_deserializer = JSONDeserializer(gps_data_schema_str, from_dict=dict_to_gpsdata)

    while True:
        try:
            messages = consumer.consume()
            if len(messages) == 0:
                continue
            messages_list = []
            for msg in messages:
                data = json_deserializer(msg.value(), SerializationContext(topic, MessageField.VALUE))
                if data is not None:
                    messages_list.append(data)
            data = {
                'status': 200,
                'code': 'new data',
                'units': messages_list
            }
            json_str = json.dumps(data)
            emit('gps data', json_str)
        except:
            pass

@socketio.on('connect')
def connect(auth):
    print('connect')
    # Connect to kafka but don't subscribe to any topic
    set_consumer_config()
    global consumer
    consumer = Consumer(config)
    #socketio.start_background_task(send_coordinate_data)
    # Get the topics name from the map
    topics = consumer.list_topics()

@socketio.on('message')
def message(auth):
    print('message event')

@socketio.on('disconnect')
def disconnect():
    global consumer
    print('disconnecting')
