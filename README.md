# ePIP

PIP - Państwowa informacja publiczna, jest projektem na przedmiot Ochrona Danych semestru 7 na Politechnice poznańskiej.
Pozwala ona na utworzenie prostej publicznej bazy danych łańcucha bloków. 
Technologia pokazana na przykładzie prostej strony internetowej, pozwalającej na sprawdzanie wydatków państwowych.

## Instalacja

Aby uruchomić aplikację potrzebny jest tylko python w wersji 3.7


## Uruchamianie peerów

Aby uruchomić jeden z peerów należy wewnątrz folderu w którym znajduje się projekt wykonać następujące komendy.
```bash
export FLASK_APP=block.py
#przykładowy port 8004
flask run --port 8004
```
Jeśli chcemy odpalić większą ilość peerów należy wykonać komendy w następujący sposób.
```bash
export FLASK_APP=block.py
#uruchamia 3 instancje, na portach 8004, 8005, 8006
flask run --port 8004 &flask run --port 8005 &flask run --port 8006 
```
Jeśli chcemy połączyć peerów w sieć wykonujemy następującą komendę
```bash
#przykład dla połączenia adresu 8004 z adresem 8005.
curl -X POST \                              
  http://127.0.0.1:8004/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8005/"}'
```

## Uruchamianie serwisu webowego

Aby uruchomić serwis webowy należy najpierw uruchomić peera, na adresie 8004, ze względu na to że strona łączy się z peerem.
Następnie wybieramy wolny port i uruchamiamy za pomocą podobnej komendy do tej opisanej wyżej. 
Należy pamiętać że trzeba przejść do folderu App.
```bash
cd App/
export FLASK_APP=views.py
#przykładowy port 8009
flask run --port 8009
```

## Wygląd strony
Przykładowy wygląd strony
![alt text](https://github.com/DalduK/OD_Projekt_Blockchain/blob/master/Screenshot.png?raw=true)


