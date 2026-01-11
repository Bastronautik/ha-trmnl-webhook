# Home Assistant TRMNL Integration

Een custom integratie voor Home Assistant waarmee je sensor entities naar TRMNL webhooks kunt sturen, inclusief historische data.

## Features

- 🔗 **Meerdere webhooks**: Configureer meerdere onafhankelijke TRMNL webhooks
- 📊 **Historische data**: Automatisch de laatste 24 uur aan data meesturen voor entities met history
- ⚙️ **Instelbaar interval**: Update interval van 5 minuten tot 24 uur
- 🎨 **UI configuratie**: Alles instelbaar via de Home Assistant UI
- 🔄 **Automatische updates**: Periodieke updates op basis van ingesteld interval
- 🛠️ **Service calls**: Handmatig updates versturen via service calls
- ⚠️ **Error handling**: Robuuste error handling met retry logic en notificaties

## Installatie

### HACS (Aanbevolen)

1. Open HACS in Home Assistant
2. Ga naar "Integrations"
3. Klik op de drie puntjes rechtsboven en selecteer "Custom repositories"
4. Voeg deze repository toe als "Integration"
5. Zoek naar "TRMNL" en installeer
6. Herstart Home Assistant

### Handmatige installatie

1. Kopieer de `custom_components/trmnl_webhook` folder naar je Home Assistant `config/custom_components/` directory
2. Herstart Home Assistant

## Configuratie

### Via UI

1. Ga naar **Instellingen** → **Apparaten & Services**
2. Klik op **+ Integratie toevoegen**
3. Zoek naar **TRMNL**
4. Voer je TRMNL Webhook ID in (te vinden in je TRMNL plugin instellingen)
5. Selecteer de sensor entities die je wilt versturen
6. Stel het update interval in (standaard 60 minuten)
7. Klik op **Verzenden**

### Meerdere webhooks toevoegen

Herhaal bovenstaande stappen om meerdere TRMNL webhooks te configureren. Elke webhook kan zijn eigen entities en update interval hebben.

### Configuratie aanpassen

1. Ga naar **Instellingen** → **Apparaten & Services**
2. Zoek de TRMNL integratie
3. Klik op **Configureren**
4. Pas de entities en/of update interval aan

## Gebruik

### Automatische updates

De integratie verstuurt automatisch updates naar je TRMNL webhook(s) op basis van het ingestelde interval.

### Handmatige updates

Je kunt ook handmatig een update versturen via een service call:

```yaml
service: trmnl_webhook.send_update
data:
  config_entry_id: "abc123def456"
```

Om de `config_entry_id` te vinden:
1. Ga naar **Ontwikkelaarshulpmiddelen** → **Services**
2. Selecteer de `trmnl_webhook.send_update` service
3. De beschikbare config entry IDs worden getoond

### In automations

```yaml
automation:
  - alias: "Verstuur TRMNL update bij temperatuurverandering"
    trigger:
      - platform: state
        entity_id: sensor.temperature_living_room
    action:
      - service: trmnl_webhook.send_update
        data:
          config_entry_id: "abc123def456"
```

## Data formaat

De integratie verstuurt de volgende JSON structuur naar je TRMNL webhook:

```json
{
  "merge_variables": {
    "timestamp": "2026-01-11T14:52:39+01:00",
    "entities": [
      {
        "entity_id": "sensor.temperature_living_room",
        "name": "Living Room Temperature",
        "state": "21.5",
        "unit": "°C",
        "attributes": {
          "device_class": "temperature",
          "friendly_name": "Living Room Temperature"
        },
        "history": [
          {"timestamp": "2026-01-10T14:52:39+01:00", "value": 20.8},
          {"timestamp": "2026-01-10T15:52:39+01:00", "value": 21.0}
        ]
      }
    ]
  }
}
```

### Historische data

Voor entities met history (opgeslagen in de recorder) wordt automatisch de data van de afgelopen 24 uur meegestuurd in het `history` veld. Dit is een array van objecten met `timestamp` en `value`.

Entities zonder history of zonder numerieke waarden krijgen geen `history` veld.

## Troubleshooting

### Webhook validatie mislukt

- Controleer of je TRMNL Webhook ID correct is
- Zorg dat je TRMNL account actief is
- Test de webhook handmatig via de TRMNL website

### Geen data ontvangen

- Controleer de logs in Home Assistant (**Instellingen** → **Systeem** → **Logs**)
- Verifieer dat de geselecteerde entities bestaan en data hebben
- Test met een handmatige update via de service call

### Error notificaties

De integratie toont notificaties in Home Assistant wanneer er problemen zijn met het versturen van data. Controleer deze notificaties voor meer details.

## Ondersteuning

Voor vragen, bugs of feature requests, open een issue op GitHub.

## Licentie

MIT License
