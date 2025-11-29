#!/bin/bash
# Quick start script for Ajna Hub

echo "🚀 Uruchamianie Ajna Hub..."
echo ""

# 1. Sprawdź czy API_KEY jest ustawiony
if [ -z "$API_KEY" ]; then
    echo "⚠️  API_KEY nie jest ustawiony!"
    echo "   Generuję tymczasowy klucz..."
    export API_KEY="dev-key-$(date +%s)"
    echo "   API_KEY=$API_KEY"
    echo ""
fi

# 2. Sprawdź czy FIREBASE_CREDENTIALS jest ustawiony
if [ -z "$FIREBASE_CREDENTIALS" ]; then
    echo "⚠️  FIREBASE_CREDENTIALS nie jest ustawiony!"
    echo "   Ustawiam domyślną ścieżkę..."
    export FIREBASE_CREDENTIALS="/home/user/-/firebase-admin.json"
fi

# 3. Wyświetl konfigurację
echo "📋 Konfiguracja:"
echo "   Working Directory: $(pwd)"
echo "   API_KEY: $API_KEY"
echo "   FIREBASE_CREDENTIALS: $FIREBASE_CREDENTIALS"
echo ""

# 4. Uruchom aplikację
echo "🎯 Uruchamiam Flask na http://127.0.0.1:8600"
echo "📊 Dashboard: http://127.0.0.1:8600/admin/dashboard?key=$API_KEY"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python app.py
