import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/"

maintenant = datetime.now()

def format_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S')

data = {
    "name": "aissam",
    "pinCode": 1234,
    "sold": 9000,
    "dernier_retrait": format_datetime(maintenant)
}

response = requests.patch(BASE_URL + "user/1", json=data)
print("Mise à jour de l'utilisateur :")
print(response.json())

response = requests.get(BASE_URL + "user/1")
print("\nRécupération de l'utilisateur :")
print(response.json())

data = {
    "name": "aissam",
    "montant": 500,
    "date": "2023-09-15T15:30:00"
}

response = requests.put(BASE_URL + "retrait/1", json=data)
print("\nAjout d'un retrait :")
print(response.json())

response = requests.get(BASE_URL + "retrait/1")
print("\nRécupération du retrait :")
print(response.json())
