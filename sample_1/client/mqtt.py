from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import time
import random

class Mqtt():
    def __init__(self, root_ca, key, cert, endpoint):
        client_id = self.__create_client_id("client_id")

        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.__mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            cert_filepath=cert,
            pri_key_filepath=key,
            client_bootstrap=client_bootstrap,
            ca_filepath=root_ca,
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=6)

        print(f"Connecting to {endpoint} with client ID '{client_id}'...")

        connected_future = self.__mqtt_connection.connect()
        connected_future.result()
        print("Connected!")

    @property
    def connection(self):
        return self.__mqtt_connection

    def publish(self, topic, payload):
        self.__mqtt_connection.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE)

    def subscribe(self, topic, callback):
        self.__mqtt_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=callback)

    def __create_client_id(self, thing_name):
        result = thing_name + '_'
        for n in [random.randint(0,10) for i in range(10)]:
            result += str(n)
        return result

    def __del__(self):
        future = self.__mqtt_connection.disconnect()
        future.add_done_callback(self.__on_disconnected)
    
    def __on_disconnected(self, disconnect_future):
        print("Disconnected.")

