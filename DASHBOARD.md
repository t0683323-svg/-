# Dashboard Administracyjny

## Przegląd
Dashboard dostępny pod `/admin/dashboard` pokazuje stan systemu w czasie rzeczywistym.

## Dostęp

### Przeglądarka (HTML)
```
http://localhost:8600/admin/dashboard?key=YOUR_API_KEY
```

### API (JSON)
```
http://localhost:8600/admin/dashboard?key=YOUR_API_KEY&format=json
```

### cURL (dla skryptów)
```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8600/admin/dashboard?format=json
```

## Wymagania

### Zależności
Dashboard wymaga dodatkowych bibliotek:
```bash
pip install psutil gitpython
```

Są one już dodane do `requirements.txt`.

### Uprawnienia
Dashboard wymaga **API key** (taki sam jak inne endpointy).

## Wyświetlane Metryki

### Sekcja 1: Status Systemu
- **Status Aplikacji**: ONLINE/OFFLINE
- **Uptime**: Czas działania od ostatniego uruchomienia
- **CPU**: Procentowe wykorzystanie procesora
- **RAM**: Wykorzystanie pamięci (procent + GB)
- **Dysk**: Zapełnienie dysku

### Sekcja 2: Dane Aplikacji
- **Urządzenia**: Liczba zarejestrowanych urządzeń w Firestore
- **Wersja**: Git commit hash (7 znaków)
- **Python**: Wersja interpretera
- **Platforma**: System operacyjny (Linux/Windows/macOS)
- **Test Coverage**: 96.19%

### Sekcja 3: Szybkie Linki
- Health Check
- JSON API
- Dokumentacja

## Przykłady Użycia

### Python
```python
import requests
import os

API_KEY = os.environ.get('API_KEY')
response = requests.get(
    'http://localhost:8600/admin/dashboard',
    params={'key': API_KEY, 'format': 'json'}
)

if response.status_code == 200:
    data = response.json()
    print(f"CPU: {data['cpu_percent']}%")
    print(f"RAM: {data['memory_percent']}%")
    print(f"Devices: {data['device_count']}")
```

### Bash/Shell
```bash
#!/bin/bash
API_KEY="your-api-key"
curl -s "http://localhost:8600/admin/dashboard?key=$API_KEY&format=json" | jq .
```

### Monitoring Script
```bash
#!/bin/bash
# monitor.sh - Check if API is healthy

API_KEY="your-key"
URL="http://localhost:8600/admin/dashboard?key=$API_KEY&format=json"

CPU=$(curl -s "$URL" | jq -r '.cpu_percent')
RAM=$(curl -s "$URL" | jq -r '.memory_percent')

if (( $(echo "$CPU > 80" | bc -l) )); then
    echo "⚠️ ALERT: High CPU usage: $CPU%"
fi

if (( $(echo "$RAM > 80" | bc -l) )); then
    echo "⚠️ ALERT: High RAM usage: $RAM%"
fi
```

## Deployment

### Lokalne Uruchomienie
```bash
export API_KEY="your-secret-key"
export FIREBASE_CREDENTIALS="/path/to/credentials.json"
python app.py
```

Następnie otwórz w przeglądarce:
```
http://localhost:8600/admin/dashboard?key=your-secret-key
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV API_KEY=your-key
ENV FIREBASE_CREDENTIALS=/app/firebase-creds.json
EXPOSE 8600
CMD ["python", "app.py"]
```

### Systemd Service
```ini
[Unit]
Description=Ajna Hub API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ajna-hub
Environment="API_KEY=your-production-key"
Environment="FIREBASE_CREDENTIALS=/opt/ajna-hub/credentials.json"
ExecStart=/usr/bin/python3 /opt/ajna-hub/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Integracja z GoDaddy

Ponieważ GoDaddy Deluxe **nie wspiera Pythona/Dockera** bezpośrednio, zalecane jest:

### Opcja A: Deployment na Railway/Render
1. Deploy aplikacji na [Railway.app](https://railway.app) (darmowy tier)
2. GoDaddy użyj do:
   - **Domena**: Wskaż A record na IP Railway
   - **SSL**: Cloudflare (darmowy SSL)
   - **Email**: Profesjonalne adresy @twoja-domena.pl

### Opcja B: VPS (DigitalOcean/Linode)
1. Kup VPS za $5/miesiąc
2. Deploy aplikacji przez Docker
3. GoDaddy DNS → VPS IP

### Opcja C: GoDaddy VPS Upgrade
- Upgrade z "Deluxe" na "VPS Hosting" (od ~$20/m)
- Pełna kontrola + Docker + Python

## Troubleshooting

### "Dashboard dependencies not installed"
```bash
pip install psutil gitpython
```

### "Unauthorized - API key required"
Upewnij się, że przekazujesz API key:
- Przez query parameter: `?key=YOUR_KEY`
- Lub header: `-H "X-API-Key: YOUR_KEY"`

### "device_count: N/A"
Firestore nie jest dostępny. Sprawdź:
- Czy `FIREBASE_CREDENTIALS` wskazuje prawidłowy plik
- Czy aplikacja ma dostęp do internetu (Firestore Cloud)

### Wysokie użycie CPU/RAM
Dashboard sam w sobie używa ~1% CPU podczas wywołania.
Jeśli widzisz wysokie wartości, sprawdź inne procesy:
```bash
top
ps aux | head -20
```

## Bezpieczeństwo

### API Key Protection
- ✅ Dashboard wymaga API key (jak inne endpointy)
- ✅ Klucz można przekazać przez header LUB query param
- ⚠️ Nie udostępniaj URL z kluczem publicznie

### Production Hardening
```python
# Opcja: Wymuś HTTPS w produkcji
if not request.is_secure and os.environ.get('ENV') == 'production':
    return redirect(request.url.replace('http://', 'https://'))
```

### Rate Limiting (Opcjonalne)
```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.headers.get('X-API-Key'))

@app.route('/admin/dashboard')
@limiter.limit("10 per minute")  # Max 10 requestów/min
def admin_dashboard():
    ...
```

## Przyszłe Rozszerzenia

Potencjalne ulepszenia dashboardu:

1. **Wykresy**: Integracja z Chart.js dla trendów CPU/RAM
2. **Alerty**: Email/SMS gdy CPU > 80%
3. **Logi**: Ostatnie 50 linii z `app.log`
4. **Kontrola**: Przyciski Start/Stop/Restart serwisów
5. **Statystyki API**: Liczba requestów, średni czas odpowiedzi
6. **Firebase Stats**: Top devices, ostatnie notyfikacje

## Status Implementacji

- ✅ Podstawowe metryki systemu (CPU, RAM, Dysk)
- ✅ Informacje o aplikacji (version, uptime, device count)
- ✅ Tryb HTML i JSON
- ✅ Autoryzacja API key
- ✅ Responsive design (Bootstrap)
- ⏳ Wykresy czasowe (TODO)
- ⏳ Panel kontrolny (Start/Stop) (TODO)
- ⏳ Real-time updates (WebSocket) (TODO)

## Support

Dashboard jest częścią głównej aplikacji. W razie problemów:
1. Sprawdź logi aplikacji
2. Sprawdź czy `psutil` i `gitpython` są zainstalowane
3. Zweryfikuj że `API_KEY` jest ustawiony
4. Sprawdź czy Firestore jest dostępny

---

**Utworzono**: 2025-01-29
**Ostatnia aktualizacja**: 2025-01-29
**Wersja**: 1.0.0
