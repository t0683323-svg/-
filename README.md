# Ajna Hub - Quick Start Guide

## 🚀 Szybkie Uruchomienie (Po Restarcie Windows)

### Opcja 1: Automatyczny Start
```bash
cd /home/user/-
./start.sh
```

### Opcja 2: Manualny Start
```bash
cd /home/user/-
export API_KEY="twoj-tajny-klucz"
export FIREBASE_CREDENTIALS="/home/user/-/firebase-admin.json"
python app.py
```

## 📍 Ważne Adresy

### Aplikacja działa na porcie **8600** (NIE 5000!)

| Endpoint | URL | Wymaga API Key |
|----------|-----|----------------|
| **Dashboard** | http://127.0.0.1:8600/admin/dashboard?key=YOUR_KEY | ✅ Tak |
| **Health Check** | http://127.0.0.1:8600/health | ❌ Nie |
| **Chat** | http://127.0.0.1:8600/chat | ✅ Tak |
| **LLM** | http://127.0.0.1:8600/llm | ✅ Tak |
| **Register Device** | http://127.0.0.1:8600/register-device | ✅ Tak |
| **Notify** | http://127.0.0.1:8600/notify | ✅ Tak |
| **Devices** | http://127.0.0.1:8600/devices | ✅ Tak |
| **Heartbeat** | http://127.0.0.1:8600/heartbeat | ✅ Tak |

## 🔑 Generowanie API Key

```bash
# Opcja 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Opcja 2: OpenSSL
openssl rand -hex 32

# Potem ustaw:
export API_KEY="wygenerowany-klucz"
```

## 📊 Dashboard

Po uruchomieniu aplikacji, otwórz w przeglądarce:

```
http://127.0.0.1:8600/admin/dashboard?key=YOUR_API_KEY
```

Zobaczysz:
- Zużycie CPU, RAM, Dysku
- Liczbę urządzeń w bazie
- Wersję aplikacji (Git commit)
- Uptime

## 🧪 Testowanie

```bash
# Uruchom wszystkie testy
./run_tests.sh

# Lub:
pytest -v

# Z coverage:
pytest --cov=. --cov-report=html
```

## 📁 Struktura Projektu

```
/home/user/-/
├── app.py                    # Główna aplikacja (PORT 8600)
├── start.sh                  # Skrypt startowy (UŻYJ TEGO!)
├── requirements.txt          # Zależności
├── firebase_init.py          # Konfiguracja Firebase
├── routes_firebase.py        # Endpointy urządzeń
├── routes_notify.py          # Endpointy notyfikacji
├── templates/
│   └── dashboard.html        # UI dashboardu
├── tests/
│   ├── test_app.py           # Testy głównej app
│   ├── test_routes_*.py      # Testy endpointów
│   └── test_security.py      # Testy bezpieczeństwa
├── TESTING.md                # Dokumentacja testów
├── SECURITY.md               # Dokumentacja bezpieczeństwa
├── DASHBOARD.md              # Dokumentacja dashboardu
└── CLIENT_INTEGRATION.md     # Przykłady klientów

```

## ⚙️ Zmienne Środowiskowe

| Zmienna | Opis | Domyślna Wartość | Wymagana? |
|---------|------|------------------|-----------|
| `API_KEY` | Klucz API do autoryzacji | - | ✅ Tak (produkcja) |
| `FIREBASE_CREDENTIALS` | Ścieżka do pliku Firebase JSON | `/home/ajna/ajna-hub/firebase-admin.json` | ⚠️ Zalecane |

## 🐛 Troubleshooting

### Problem: "Connection refused" lub "Cannot connect"
**Rozwiązanie:** Aplikacja nie jest uruchomiona
```bash
cd /home/user/-
./start.sh
```

### Problem: "Unauthorized"
**Rozwiązanie:** Brakuje API key
```bash
# W przeglądarce dodaj: ?key=YOUR_KEY
http://127.0.0.1:8600/admin/dashboard?key=YOUR_KEY
```

### Problem: "No module named 'psutil'"
**Rozwiązanie:** Zainstaluj zależności
```bash
pip install -r requirements.txt
```

### Problem: "FileNotFoundError: firebase-admin.json"
**Rozwiązanie:** Ustaw prawidłową ścieżkę
```bash
export FIREBASE_CREDENTIALS="/home/user/-/firebase-admin.json"
```

### Problem: Port 8600 już zajęty
**Rozwiązanie:** Zabij poprzedni proces
```bash
# Znajdź proces
lsof -i :8600

# Zabij proces (wstaw PID z poprzedniej komendy)
kill -9 PID
```

## 🔧 Konfiguracja Windows (WSL)

Jeśli używasz Windows + WSL:

1. **Otwórz WSL Terminal:**
   ```bash
   wsl
   ```

2. **Przejdź do projektu:**
   ```bash
   cd /home/user/-
   ```

3. **Uruchom:**
   ```bash
   ./start.sh
   ```

4. **W przeglądarce Windows:**
   ```
   http://127.0.0.1:8600/admin/dashboard?key=YOUR_KEY
   ```

## 📦 Deployment

### Lokalne (Development)
- Użyj `start.sh`
- Port: 8600
- API_KEY: dowolny (do testów)

### Produkcyjne (Railway/Render)
- Zobacz: `DEPLOYMENT.md` (TODO)
- Ustaw `API_KEY` w sekretach
- Skonfiguruj `FIREBASE_CREDENTIALS`

## 📚 Dokumentacja

| Plik | Opis |
|------|------|
| `README.md` | Ten plik - quick start |
| `TESTING.md` | Jak uruchomić testy (47 testów, 96% coverage) |
| `SECURITY.md` | Bezpieczeństwo i API key |
| `DASHBOARD.md` | Dashboard i monitoring |
| `CLIENT_INTEGRATION.md` | Jak podłączyć klientów (Python, Node, ESP32) |

## 🎯 Status Projektu

- ✅ **Test Coverage:** 96.19% (47 testów)
- ✅ **Security:** API Key authentication
- ✅ **CI/CD:** GitHub Actions
- ✅ **Dashboard:** Admin panel
- ✅ **Dokumentacja:** Kompletna

## 🆘 Pomoc

Jeśli coś nie działa:

1. Sprawdź czy aplikacja jest uruchomiona: `ps aux | grep python`
2. Sprawdź logi: aplikacja wyświetla błędy w terminalu
3. Zweryfikuj port: **8600**, nie 5000!
4. Sprawdź API key: musi być ustawiony w `?key=` lub `X-API-Key` header

## 🚀 Następne Kroki

Po uruchomieniu lokalnie:
1. [ ] Przetestuj dashboard: http://127.0.0.1:8600/admin/dashboard?key=YOUR_KEY
2. [ ] Uruchom testy: `./run_tests.sh`
3. [ ] Skonfiguruj GoDaddy DNS (domena)
4. [ ] Deploy na Railway/Render (hosting aplikacji)

---

**Port:** 8600 (NIE 5000!)
**Projekt:** /home/user/-
**Skrypt startowy:** ./start.sh
