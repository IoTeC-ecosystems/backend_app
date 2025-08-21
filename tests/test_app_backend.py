import uuid
import random
import time
import json
from datetime import datetime

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

from backend_app.config import config, sr_config
from backend_app.schemas_objects import GPSData, gpsdata_to_dict
from backend_app.schema import gps_data_schema_str
from backend_app.utils import is_valid_uuid

def create_topics_produce_data():
    admin = AdminClient(config)
    topics = [str(uuid.uuid4()) for _ in range(10)]
    new_topics = [NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topics]
    # Create topics
    fs = admin.create_topics(new_topics)

    # Wait for operations to complete
    for topic, f in fs.items():
        try:
            f.result()
        except:
            pass

    schema_registry_client = SchemaRegistryClient(sr_config)
    json_serializer = JSONSerializer(gps_data_schema_str, schema_registry_client, gpsdata_to_dict)
    producer = Producer(config)
    for unit in topics:
        data = []
        for _ in range(10):
            data.append(GPSData(unit, random.random(), random.random(),
                                random.random(), random.random(), datetime.now().timestamp()))
        for d in data:
            producer.produce(topic=unit, key=str(time.time()),
                             value=json_serializer(d, SerializationContext(unit, MessageField.VALUE)))
        producer.flush()


def delete_test_topics():
    admin = AdminClient(config)
    topics = admin.list_topics()

    to_be_deleted = []
    for topic in topics.topics.keys():
        if is_valid_uuid(topic):
            to_be_deleted.append(topic)

    fs = admin.delete_topics(to_be_deleted)
    # Wait for operation to finish
    for topic, f in fs.items():
        try:
            f.result()
        except:
            pass

def test_socketio_events(socketio_client):
    #create_topics_produce_data()

    # Get data from connect event
    resp = socketio_client.get_received()
    data = resp[0]['args'][0]['data']
    assert 'status' in data
    assert 'code' in data
    assert 'available units' in data
    assert 'units' in data

    units = json.loads(data)
    assert units['status'] == 200
    assert units['code'] == 'available units'

    # Send an empty list
    data = {
        'units': [],
    }
    socketio_client.emit('subscribe', json.dumps(data))
    resp = socketio_client.get_received()
    data = resp[0]['args'][0]
    assert resp[0]['name'] == 'error'
    assert 'status' in data
    assert '400' in data
    assert 'code' in data
    assert 'empty list of units' in data

    # Send an invalid topic id
    data = {
        'units': ['invalid_topic', 'another_invalid_topic']
    }
    socketio_client.emit('subscribe', json.dumps(data))
    resp = socketio_client.get_received()
    data = resp[0]['args'][0]
    assert resp[0]['name'] == 'error'
    assert '400' in data
    assert 'non existing units' in data
    assert 'invalid_topic' in data
    assert 'another_invalid_topic' in data

    # Send valid topics
    units_list = [unit['unit'] for unit in units['units']]
    data = {
        'units': units_list
    }
    socketio_client.emit('subscribe', json.dumps(data))
    resp = socketio_client.get_received()
    data = resp[0]['args'][0]
    assert resp[0]['name'] == 'error'
    assert 'status' in data
    assert 'code' in data
    assert 'subscribed' in data

    time.sleep(15)

    resp = socketio_client.get_received()
    for data in resp:
        assert 'gps data' == data['name']
        assert '200' in data['args'][0]
        assert 'new data' in data['args'][0]
        json_obj = json.loads(data['args'][0])
        unit = json_obj['units'][0]['uuid']
        assert unit in units_list

    #delete_test_topics()
