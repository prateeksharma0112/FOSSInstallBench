## 📦 Installation

### Voraussetzungen

- Node.js 18 oder höher
- Bun (empfohlen) oder npm/yarn

### Schritte

```bash
# Repository klonen
git clone …/ki-fuehrerschein.git

# In das Verzeichnis wechseln
cd ki-fuehrerschein

# Abhängigkeiten installieren
bun install

# Entwicklungsserver starten
bun dev
```

Die Anwendung ist dann unter [http://localhost:5173](http://localhost:5173) erreichbar.

## ⚙️ Konfiguration

### Umgebungsvariablen

Erstellen Sie eine `.env.local` Datei basierend auf der Vorlage:

```bash
cp .env.example .env.local
```

Verfügbare Umgebungsvariablen:

| Variable      | Beschreibung               | Erforderlich |
| ------------- | -------------------------- | ------------ |
| `MONGODB_URI` | MongoDB Verbindungs-URI    | Optional\*   |
| `MONGODB_DB`  | Name der MongoDB Datenbank | Optional\*   |

\*Die MongoDB-Verbindung ist nur erforderlich, wenn die Metriken-Funktionalität genutzt werden soll.
