# RAG Demo - Implementazione Minimale

Un'implementazione minimale di RAG (Retrieval Augmented Generation) per scopi educativi, che include:

- 🤖 Interfaccia chat con assistente AI
- 🔍 Ricerca documenti con RAG tramite chiamate di funzione
- 📚 Database vettoriale ChromaDB
- ⚡ Backend FastAPI
- 🎨 Frontend semplice HTML/CSS/JS
- 🔧 Integrazione GPT-4.1 Mini

**Realizzato da [Davide Pasca](https://github.com/dpasca) presso [NEWTYPE K.K.](https://newtypekk.com), Giappone**

![Screenshot RAG Demo](assets/screenshot01.png)

## Configurazione Rapida

**Opzione 1: Configurazione Automatica (Consigliata)**
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

**Opzione 2: Configurazione Manuale**

1. **Creare e attivare un ambiente virtuale:**
   ```bash
   # Creare ambiente virtuale
   python -m venv venv

   # Attivare ambiente virtuale
   # Su Linux/Mac:
   source venv/bin/activate
   # Su Windows:
   venv\Scripts\activate
   ```

2. **Installare le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurare le variabili d'ambiente:**
   - Copiare `.env.example` in `.env` e aggiungere la chiave API OpenAI:
   ```bash
   cp .env.example .env
   # Modificare .env e aggiungere la chiave API OpenAI
   ```

4. **Inizializzare il database RAG:**
   ```bash
   python update_rag.py
   ```

5. **Avviare il server:**
   ```bash
   python main.py
   ```

6. **Aprire il browser:**
   Navigare su `http://localhost:8000`

> **Nota**: Lo script di configurazione automatica creerà l'ambiente virtuale, installerà le dipendenze e configurerà il file `.env` per te. Dovrai solo aggiungere la tua chiave API OpenAI al file `.env`.

## Utilizzo

### Interfaccia Chat
- Porre domande nell'interfaccia web
- L'AI cercherà automaticamente nei documenti quando pertinente
- Le fonti vengono visualizzate quando viene utilizzato RAG

### Aggiungere Documenti
- Posizionare file `.txt` nella cartella `documents/`
- Eseguire `python update_rag.py` per aggiornare il database
- I documenti vengono suddivisi in chunk con dimensione/sovrapposizione configurabili

### Configurazione
Regolare le impostazioni in `.env`:

**Configurazione LLM:**
- `OPENAI_API_KEY`: La tua chiave API OpenAI (richiesta)
- `OPENAI_BASE_URL`: URL base API (lasciare vuoto per OpenAI, impostare per altri provider)
- `LLM_MODEL`: Modello linguistico da utilizzare (predefinito: gpt-4.1-mini)

**Configurazione RAG:**
- `EMBEDDING_MODEL`: Modello di embedding OpenAI da utilizzare (predefinito: text-embedding-3-small)
- `CHUNK_SIZE`: Dimensione dei chunk di testo (predefinito: 1000)
- `CHUNK_OVERLAP`: Sovrapposizione tra chunk (predefinito: 200)
- `TOP_K_RESULTS`: Numero di chunk da recuperare (predefinito: 5)

**Modelli disponibili:**
- **Modelli LLM**: `gpt-4.1-mini`, `gpt-4.1`, o qualsiasi modello compatibile con OpenAI
- **Modelli di Embedding**: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`

**Utilizzo con altri provider:**
```bash
# Per Ollama (locale)
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2
OPENAI_API_KEY=ollama  # Può essere qualsiasi valore per Ollama

# Per altre API compatibili con OpenAI
OPENAI_BASE_URL=https://your-provider.com/v1
LLM_MODEL=your-model-name
OPENAI_API_KEY=your-api-key
```

## Architettura

```
├── main.py              # App FastAPI
├── chat.py              # Logica chat con OpenAI
├── rag.py               # Sistema RAG con ChromaDB
├── models.py            # Modelli Pydantic
├── update_rag.py        # Script di elaborazione documenti
├── documents/           # File di testo per RAG
├── frontend/            # Interfaccia web
│   ├── index.html
│   ├── script.js
│   └── style.css
└── chroma_db/          # Database vettoriale (creato automaticamente)
```

## Caratteristiche Principali

- **RAG basato su tool**: Utilizza le chiamate di funzione OpenAI per attivare la ricerca documenti
- **Attribuzione delle fonti**: Mostra quali documenti e chunk sono stati utilizzati
- **Chunking configurabile**: Regola dimensione chunk e sovrapposizione tramite variabili d'ambiente
- **Archiviazione locale**: ChromaDB funziona localmente con archiviazione persistente
- **Focus educativo**: Codice pulito e leggibile con complessità minima

## Dettagli Tecnici

Per la documentazione tecnica dettagliata sull'implementazione RAG, vedere [TECHNICAL_it.md](TECHNICAL_it.md). Copre dettagli implementativi, decisioni di design e come estendere il sistema.

## Lingue

- [English README](README.md)
- [日本語 README](README_ja.md)
- [Italiano README](README_it.md)
- [English Technical Docs](TECHNICAL.md)
- [日本語技術ドキュメント](TECHNICAL_ja.md)
- [Documentazione Tecnica Italiana](TECHNICAL_it.md)

## Sviluppo

### Configurazione Alternativa con uv (Avanzata)
Per una gestione più veloce delle dipendenze, puoi utilizzare [uv](https://github.com/astral-sh/uv):
```bash
# Installare uv se non già fatto
pip install uv

# Creare e attivare ambiente virtuale
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# Installare dipendenze
uv pip install -r requirements.txt
```