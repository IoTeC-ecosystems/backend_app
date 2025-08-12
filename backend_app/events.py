import json
import uuid

# Flask
from flask import session
from flask_socketio import emit, send

# Kafka
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

from .schemas_objects import GPSData, dict_to_gpsdata, gpsdata_to_dict
from .schema import gps_data_schema_str
from .config import config
from .utils import is_valid_uuid

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

    # Getting data from kafka
    while True:
        # Number of topics might change with time
        topics = consumer.list_topics()
        topics_list = [topic for topic in topics.topics.keys() if is_valid_uuid(topic)]
        num_topics = len(topics_list)
        try:
            # Try to get one message per topic
            events = consumer.consume(num_messages=num_topics, timeout=1)
            if len(events) == 0:
                continue
            messages_list = []
            for evt in events:
                data = json_deserializer(evt.value(), SerializationContext(evt.topic(), MessageField.VALUE))
            if data is not None:
                messages_list.append(gpsdata_to_dict(data, None))
            data = {
                'status': 200,
                'code': 'new data',
                'units': messages_list
            }
            json_str = json.dumps(data)
            socketio.emit('gps data', json_str)
        except Exception as e:
            pass


@socketio.on('connect')
def connect(auth):
    # Connect to kafka but don't subscribe to any topic
    set_consumer_config()
    global consumer
    consumer = Consumer(config)
    # Get the topics name from the map
    topics = consumer.list_topics()
    topics_list = []
    for topic in topics.topics.keys():
        if is_valid_uuid(topic):
            topics_list.append({'unit': topic})
    data = {
        'status': 200,
        'code': 'available units',
        'units': topics_list
    }
    json_str = json.dumps(data)
    # Send to client
    emit('units', {'data': json_str})

    # Start background task for gps data
    socketio.start_background_task(target=send_coordinate_data)


@socketio.on('subscribe')
def subscribe(_json):
    global consumer
    # Get the list of topics to subscribe
    data = json.loads(_json)
    if len(data['units']) == 0:
        err_obj = {
            'status': 400,
            'code': 'empty list of units'
        }
        json_str = json.dumps(err_obj)
        emit('error', json_str)

    # Validate topics
    topics_list = consumer.list_topics()
    topics = set()
    for topic in topics_list.topics.keys():
        topics.add(topic)
    invalid_topics = []
    valid_topics = []
    for unit in data['units']:
        if unit not in topics:
            invalid_topics.append(unit)
        else:
            valid_topics.append(unit)
    if len(invalid_topics) > 0:
        err_obj = {
            'status': 400,
            'code': 'non existing units',
            'units': invalid_topics
        }
        emit('error', json.dumps(err_obj))
    try:
        consumer.subscribe(valid_topics)
        err_obj = {
            'status': 200,
            'code': 'subscribed'
        }
        emit('error', json.dumps(err_obj))
    except KafkaException:
        # Handle case
        pass


@socketio.on('message')
def message(auth):
    print('message event')


@socketio.on('disconnect')
def disconnect():
    global consumer
    print('disconnecting')
