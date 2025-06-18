import requests
from kafka import KafkaProducer
import json
import time
import uuid
# create timestamp
from datetime import datetime

producer = KafkaProducer(bootstrap_servers='34.76.159.192:9092',
                            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                            key_serializer=lambda v: json.dumps(v).encode('utf-8')
                            )

response = requests.get("http://hasanadiguzel.com.tr/api/kurgetir")
data = response.json()
print(data["TCMB_AnlikKurBilgileri"])



def get_data():
    response = requests.get("http://hasanadiguzel.com.tr/api/kurgetir")
    data = response.json()
    return data["TCMB_AnlikKurBilgileri"]

while True:
    data = get_data()
    for row in data:
        row["id"] = str(uuid.uuid4())
        row["Tarih"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(5)
        producer.send(
            'kur',
            value=row
            )
        producer.flush()
        print("mesaj gönderildi")
        print(row)