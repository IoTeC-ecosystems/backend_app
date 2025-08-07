import uuid
import random
import time

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
                                random.random(), random.random(), '05082025 17:30'))
        for d in data:
            producer.produce(topic=unit, key=d.uuid,
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

def test_connect_event(socketio_client):
    create_topics_produce_data()

    # Connect event
    #socketio_client.connect()
    resp = socketio_client.get_received()
    data = resp[0]['args'][0]['data']
    assert 'status' in data
    assert 'code' in data
    assert 'available units' in data
    assert 'units' in data

    delete_test_topics()
