# ROBPLAN INSIGHT
![image](https://github.com/patricuj/RobPlan-UiT/assets/125909221/36baa8c7-e0b6-43eb-a030-42f7aefec9cf)

##
ROBPLAN INSIGHT er et dashboard utviklet i samarbeid med SINTEF og Equinor. for å integreres med Equinors [ISAR](https://github.com/equinor/isar) (Integration and Supervisory control of Autonomous Robots), som håndterer integrasjon av robotapplikasjoner i operatørsystemer. Gjennom ISAR API kan man sende kommandoer til en robot for å utføre oppdrag og samle inn resultater.

ROBPLAN INSIGHT er et resultat av et bachelorprosjekt (DTE-2781 Bacheloroppgave i datateknikk)
med SINTEF og Equinor som oppdragsgivere.

Utviklet av Bachelorgruppe 16 ved UiT Norges arktiske universitet, våren 2024.

## Lokal Utvikling

***MERK:*** Dashboardet er blitt utviklet på Ubuntu 20.04 gjennom hele prosjektets gang og alle resultater produsert i bacheloroppgaven er basert på dette operativsystemet. Dashboardet har blitt installert og testet i Windows og, der alt fungerer utenom **Historikk**. Dette er på grunn av forskjell i hvordan dataene håndteres mellom Ubuntu og Windows.


For å sette opp et lokalt utviklingsmiljø må repositoryen forkes:

1. **Fork repoet:**
   Trykk på "+ Create a new fork" for å lage din egen kopi av repoet.

2. **Klon repoet:**
   Klon din forkede repo til din lokale maskin ved å kjøre følgende kommando i terminalen:
   ```
   git clone https://github.com/<ditt-brukernavn>/RobPlan-UiT
   cd RobPlan-UiT
   ```

## Oppsett av Docker Container

For å sette opp og kjøre MariaDB og phpMyAdmin som Docker-containere for webapplikasjonen:

1. Naviger til mappen der `docker-compose.yml`-filen ligger.
### Linux
Kjør kommando:
    ```
    docker compose up -d
    ```
### Windows
Kjør kommando:
    ```
    docker-compose up -d
    ```
#### phpMyAdmin
Etter oppsett av docker containeren kan du administrere databasen via http://localhost:8082/

**Username:** user

**Password:** test

Trykk på SQL øverst og kjør scriptet i [Datamodel.sql](https://github.com/patricuj/RobPlan-UiT/blob/main/Database/Datamodel.sql)

Deretter kjør scriptet i [Data.sql](https://github.com/patricuj/RobPlan-UiT/blob/main/Database/Data.sql)

## Virtuelt miljø

### Linux

1. Opprett det virtuelle miljøet:

    ```
    python -m venv venv
    ```

2. Aktiver det virtuelle miljøet:

    ```
    source venv/bin/activate
    ```

### Windows

1. Opprett det virtuelle miljøet:

    ```
    python -m venv venv
    ```[ISAR](https://github.com/equinor/isar) 
### Installasjon av ISAR og isar-robot:
ROBPLAN INSIGHT er designet for å jobbe med ISAR. Følg instruksjonene i de respektive repoene for å installere Equinors [ISAR](https://github.com/equinor/isar) og [isar-robot](https://github.com/equinor/isar-robot)

Merk: Dashboardet har ikke blitt testet med ISAR kjørt på Docker, men fungerer med ISAR kjørt lokalt.

#### Generell veiledning til installasjon av ISAR og isar-robot
1. Lag en fork av [ISAR](https://github.com/equinor/isar) 
2. Deretter klon og installer ISAR slik:
```
git clone https://github.com/<brukernavn>/isar
cd isar
pip install -e .[dev]
```
Installer så isar-robot med kommadoen:
```
pip install isar-robot
```

Etter installasjon av ISAR og isar-robot må du navigere til ISAR sin [settings.env](https://github.com/equinor/isar/blob/main/src/isar/config/settings.env) fil og sette følgende:
```
ISAR_MQTT_SSL_ENABLED = false
```
Dette er nødvendig for å deaktivere SSL for MQTT-kommunikasjon da standardoppsettet for ROBPLAN INSIGHT ikke inkluderer SSL-konfigurasjon for MQTT.

### Installere MQTT-broker

For at dashboardet skal kunne abonnere på emner fra ISAR, må du installere en MQTT-broker som Mosquitto:

### Linux

1. Oppdater pakkelisten og installer Mosquitto og Mosquitto-klienter:
```
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients
```
2. Start Mosquitto-tjenesten og sett den til å starte automatisk ved oppstart:
```
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```
### Windows

1. Last ned [Mosquitto](https://mosquitto.org/download/).
2. Følg installasjonsinstruksjonene for Windows.
3. Start Mosquitto-tjenesten ved å navigere til installasjonsmappen, default path er C:\Program Files\mosquitto og kjør kommandoen 
```
mosquitto.exe -v 
```


#### MQTT-klient
For å overvåke MQTT-meldinger, anbefales det å bruke MQTT Explorer:

1. Last ned [MQTT Explorer](https://mqtt-explorer.com/).
2. Installer og konfigurer klienten til å koble til din lokale Mosquitto-broker.
3. Legg til en ny connection + og fyll inn følgende:
   - Name: Valgfritt navn
   - Host: localhost
   - Port: 1883
   - Username: isar
   - Password:

Husk å skru av Encryption (tls).

![image](https://github.com/patricuj/RobPlan-UiT/assets/125909221/9846c639-9d14-48cf-b02c-3fc6a68317d3)


## Oppsett av selvsignert SSL-sertifikat for lokal utvikling

### Linux

Før du kjører applikasjonen, må du opprette et SSL-sertifikat for å kunne kjøre serveren over HTTPS:

1. Installer OpenSSL med kommandoen 
```
sudo apt-get install openssl
```
2. Åpne terminalen og naviger til mappen hvor du ønsker å lagre sertifikatene.
3. Kjør følgende kommando for å generere en privat nøkkel og et offentlig sertifikat:
   ```
   openssl genrsa -out server.key 2048
   openssl req -new -x509 -key server.key -out server.crt -days 365
   ```
Under prosessen, vil du bli bedt om å oppgi informasjon for sertifikatet. Disse kan være vilkårlige for lokal utvikling.

### Windows

1. Installer OpenSSL fra [slproweb.com](https://slproweb.com/products/Win32OpenSSL.html).
2. Åpne OpenSSL og naviger til mappen hvor du ønsker å lagre sertifikatene.
3. Kjør følgende kommando for å generere en privat nøkkel og et offentlig sertifikat:
   ```
   openssl genrsa -out server.key 2048
   openssl req -new -x509 -key server.key -out server.crt -days 365
   ```

Under prosessen, vil du bli bedt om å oppgi informasjon for sertifikatet. Disse kan være vilkårlige for lokal utvikling.

## Opprette en `.env`-fil
For å konfigurere applikasjonen til å bruke SSL-sertifikater og hente resultatene fra ISAR, må du opprette en .env-fil i prosjektets rotmappe. Denne filen brukes til å sette miljøvariabler som applikasjonen vil lese ved oppstart.

### Linux og Windows
Opprett en .env-fil i prosjektets rotmappe og legg til følgende miljøvariabler:

```
export SSL_CERT_PATH="/path/to/your/server.crt"
export SSL_KEY_PATH="/path/to/your/server.key"
export RESULTS_DIR="/path/to/isar/results"
```
For eksempel:
```
export SSL_CERT_PATH="/home/dennis/RobPlan-UiT/server.crt"
export SSL_KEY_PATH="/home/dennis/RobPlan-UiT/server.key"
export RESULTS_DIR="/home/dennis/isar/results"
```

## Kjøre ROBPLAN INSIGHT og ISAR
Nå som alt er konfigurert, kan vi kjøre ISAR og ROBPLAN INSIGHT.

### Kjøre ISAR
1. Åpne en ny terminal eller IDE:
   Naviger til ISAR-prosjektets rotmappe.
2. Start ISAR:
   Kjør følgende kommando:
   ```
   python main.py
   ```
   Dette vil starte ISDAR og opprette en isar-robot med navnet "Placebot"

#### Legge til flere robter
Hvis du ønsker å legge til flere roboter, må du endre [settings.py](https://github.com/equinor/isar/blob/main/src/isar/config/settings.py) i ISAR.
1. Sett en ny `API_PORT`:
   
   På linje 81, sett en ny port for API-en
   ```
   API_PORT: int = Field(default=3001)
   ```
2. Sett et nytt ROBOT_NAME:
   
   På linje 184, sett et nytt navn for roboten.
   ```
   ROBOT_NAME: str = Field(default="Placebot 2")
   ```
3. Sett en ny ISAR_ID:
   
   På linje 187, sett en ny unik ID for ISAR-instansen.
   ```
   ISAR_ID: str = Field(default="00000000-0000-0000-0000-000000000001")
   ```
### Kjøre ROBPLAN INSIGHT
1. Naviger til RobPlan-UiT sin rotmappe.
2. Husk at det virtuelle miljøet må være aktivert.
    
  ```
  python manage.py
  ```
Du kan nå åpne dashboardet i en nettleser gjennom https://127.0.0.1:5000/

Merk:
Når du prøver å få tilgang til applikasjonen via HTTPS, kan du få en advarsel som sier:

"Your connection is not private
NET::ERR_CERT_AUTHORITY_INVALID"

Dette er normalt når man bruker et selvsignert sertifikat. For å fortsette til applikasjonen, kan du trykke på "Advanced" og deretter "Proceed to 127.0.0.1 (unsafe)".

Du kan nå logge inn og begynne!

Brukernavn: testbruker

Passord: test


## Mediakrediteringer

- [ROBOT](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/ROBOT.jpg)- <a href="https://www.freepik.com/free-vector/graident-ai-robot-vectorart_125887871.htm#query=robot&position=1&from_view=keyword&track=sph&uuid=c0e8a7e5-c537-49a0-a1d0-46b043e8263e">Image by juicy_fish</a> on Freepik
- [Bakgrunnsbilde innlogging](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/robot.jpg)- Fritt å bruke uten kreditering. Hentet fra [Freepik.com](https://www.freepik.com/free-vector/abstract-realistic-technology-particle-background_6674339.htm#fromView=search&page=1&position=27&uuid=64310dea-24a2-46b7-b064-d17f50662932)
- [Facility_map](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/Facility_map.png), [replan_mission.jpg](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/replan_mission.jpg) og [robotoverview.png](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/robot.png) er hentet fra [Gazebo Turtleworld](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/).
-  [current_mission.jpg](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/current_mission.jpg), [electric_box.jpg](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/electric_box.jpg) og [example_audio.wav](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/example_audio.wav) er hentet fra [ISAR](https://github.com/equinor/isar) og [isar-robot](https://github.com/equinor/isar-robot).
- [Logo](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/Logo.png)/[Logo1](https://github.com/patricuj/RobPlan-UiT/blob/main/app/static/Logo1.png) er designet av oss utviklere av ROBPLAN INSIGHT.