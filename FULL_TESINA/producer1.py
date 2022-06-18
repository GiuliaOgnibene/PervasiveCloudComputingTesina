import json
from secret import mqtt_user, mqtt_password, broker_ip, broker_port, default_topic, utente1
import paho.mqtt.client as mqtt
import time

client_id = utente1

mqtt_client = mqtt.Client(client_id)
print("Connecting to " + broker_ip + " port: " + str(broker_port))
mqtt_client.username_pw_set(username=mqtt_user, password=mqtt_password)
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()

for r in open('accel1.csv'):
    r = r.strip()
    t, acc = r.split(',')
    payload_ = json.dumps({'sensor': client_id, 'time': t, 'acc': acc})
    infot = mqtt_client.publish(default_topic, payload_)
    infot.wait_for_publish()
    print('Message sent \t\t', 'time:', t, '\t\t acc:', acc)
    time.sleep(1)

mqtt_client.loop_stop()
