from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from secret import bot_token, broker_ip, broker_port, mqtt_user, mqtt_password, default_topic
import secret
import json
import paho.mqtt.client as mqtt
import telegram_send
from google.cloud import firestore

logged_user = []


def welcome(update, context):
    global client
    user = update.message.from_user
    if user['id'] not in logged_user:
        msg = "Benvenuto! Inserire la password per autenticarsi "
        update.message.reply_text(msg, parse_mode='HTML')
    else:
        msg = "Benvenuto!"
        update.message.reply_text(msg, parse_mode='HTML')


def process_chat(update, context):
    user = update.message.from_user
    message = update.message.text.lower()
    if message == secret.password1:
        logged_user.append(user['id'])
        update.message.reply_text("Benvenuto! Hai appena effettuato il login per l'utente " + secret.utente1)
    elif message == secret.password2:
        logged_user.append(user['id'])
        update.message.reply_text("Benvenuto! Hai appena effettuato il login per l'utente " + secret.utente2)


def on_connect(self, client, userdata, rc):
    print("Connesso con risultato " + str(rc))
    self.subscribe(default_topic)
    print("Sottoscritto agli eventi di: " + default_topic)


def on_message(client, userdata, msg):
    msg = json.loads(msg.payload.decode("utf-8"))
    db = firestore.Client.from_service_account_json('credentials.json')
    db.collection(msg['sensor']).document(msg['time']).set({'time': msg['time'], 'value': msg['acc']})
    print(msg)
    for i in msg['acc']:
        i = int(i)
        treshold = 9
        if i >= treshold and msg['sensor'] == 'Nonno':
            telegram_send.send(messages=["<b>ATTENZIONE!</b> Il " + msg['sensor'] + " è caduto"], parse_mode='HTML')
            # telegram_send.send(messages=["La caduta è avvnuta con accelerazione " + str(i) + " m/s2"])
        elif i >= treshold and msg['sensor'] == 'Nonna':
            telegram_send.send(messages=["<b>ATTENZIONE!</b> La " + msg['sensor'] + " è caduta"], parse_mode='HTML')
            # telegram_send.send(messages=["La caduta è avvnuta con accelerazione " + str(i) + " m/s2"])
    print('Accelerazione: ', msg['acc'])


def main():
    global client
    print('BOT AVVIATO!')

    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", welcome))
    dp.add_handler(MessageHandler(Filters.regex('^.*$'), process_chat))

    client_id = "sensori"
    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=mqtt_user, password=mqtt_password)
    client.connect(broker_ip, broker_port)
    client.loop_forever()

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
