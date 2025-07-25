# Documentazione Tecnica: Implementazione RAG Demo

Questo documento fornisce una spiegazione tecnica dettagliata di come è implementato il sistema RAG (Retrieval Augmented Generation). È progettato per sviluppatori Python che comprendono lo sviluppo web ma sono nuovi ai concetti RAG.

## Indice
1. [Panoramica Architettura](#panoramica-architettura)
2. [Sistema RAG Spiegato](#sistema-rag-spiegato)
3. [Dettagli Implementazione](#dettagli-implementazione)
4. [Walkthrough del Codice](#walkthrough-del-codice)
5. [Decisioni Chiave di Design](#decisioni-chiave-di-design)
6. [Argomenti Avanzati](#argomenti-avanzati)

## Panoramica Architettura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   OpenAI API    │
│   (HTML/CSS/JS) │◄──►│   Backend       │◄──►│   (GPT-4.1 Mini)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Sistema RAG   │◄──►│   ChromaDB      │
                       │   (rag.py)      │    │   (Vector DB)   │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Documenti     │
                       │   (file .txt)   │
                       └─────────────────┘
```

## Sistema RAG Spiegato

### Cos'è RAG?

RAG (Retrieval Augmented Generation) è una tecnica che potenzia i Large Language Models (LLM) fornendo loro accesso a conoscenza esterna. Invece di affidarsi solo ai dati di addestramento, il modello può "recuperare" informazioni rilevanti da una base di conoscenza per "aumentare" le sue risposte.

### Come Funziona il Nostro RAG

1. **Elaborazione Documenti**: I documenti di testo vengono divisi in chunk e convertiti in embedding vettoriali
2. **Archiviazione**: Gli embedding vengono memorizzati in ChromaDB (database vettoriale)
3. **Tempo di Query**: Le domande dell'utente vengono convertite in embedding e confrontate con i chunk memorizzati
4. **Recupero**: I chunk più simili vengono recuperati e forniti al LLM
5. **Generazione**: Il LLM genera risposte utilizzando sia il suo addestramento che il contesto recuperato

## Dettagli Implementazione

### Componenti Principali

#### 1. Elaborazione Documenti (`rag.py`)

```python
# Divisione testo con sovrapposizione per preservare contesto
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=self.chunk_size,      # Predefinito: 1000 caratteri
    chunk_overlap=self.chunk_overlap, # Predefinito: 200 caratteri
    length_function=len,
)
```

**Perché il chunking?**
- Gli LLM hanno limiti di token
- Chunk più piccoli migliorano la precisione del recupero
- La sovrapposizione preserva il contesto tra i confini

#### 2. Embedding Vettoriali

```python
# Utilizzo del modello di embedding più recente di OpenAI
self.embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
)
```

**Perché gli embedding?**
- Convertono il testo in vettori numerici
- Abilitano la ricerca per similarità semantica
- "Machine learning" e "Algoritmi AI" hanno embedding simili

#### 3. Database Vettoriale (ChromaDB)

```python
# Archiviazione locale persistente
self.client = chromadb.PersistentClient(path="./chroma_db")
self.collection = self.client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # Similarità coseno per testo
)
```

**Perché ChromaDB?**
- Ricerca rapida per similarità con indicizzazione HNSW
- Archiviazione persistente (sopravvive ai riavvii)
- API semplice per scopi educativi

#### 4. Integrazione RAG Basata su Tool (`chat.py`)

```python
# Definizione OpenAI Function Calling
RAG_TOOL = {
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": "Cerca nella base di conoscenza dei documenti",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La query di ricerca per trovare documenti rilevanti"
                }
            },
            "required": ["query"]
        }
    }
}
```

**Perché le chiamate di funzione?**
- Lascia che l'AI decida quando utilizzare RAG
- Integrazione naturale con il flusso conversazionale
- Evita ricerche non necessarie per domande non correlate

## Walkthrough del Codice

### 1. Processo di Ingestione Documenti

```python
def add_documents(self, documents_dir: str = "documents"):
    # 1. Pulisce documenti esistenti
    all_items = self.collection.get()
    if all_items['ids']:
        self.collection.delete(ids=all_items['ids'])

    # 2. Elabora ogni file .txt
    for filename in os.listdir(documents_dir):
        if filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # 3. Divide in chunk
            chunks = self.text_splitter.split_text(content)

            # 4. Crea metadati per ogni chunk
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "filename": filename,
                    "chunk_index": i
                })

    # 5. Genera embedding e memorizza
    embeddings = self.embeddings.embed_documents(all_chunks)
    self.collection.add(
        embeddings=embeddings,
        documents=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids
    )
```

### 2. Processo di Query

```python
def query(self, query: str, top_k: int = None) -> List[RAGChunk]:
    # 1. Converte query in embedding
    query_embedding = self.embeddings.embed_query(query)

    # 2. Cerca vettori simili
    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k or self.top_k
    )

    # 3. Converte risultati in formato strutturato
    chunks = []
    for i, doc in enumerate(results['documents'][0]):
        metadata = results['metadatas'][0][i]
        chunks.append(RAGChunk(
            content=doc,
            filename=metadata['filename'],
            chunk_index=metadata['chunk_index']
        ))

    return chunks
```

### 3. Integrazione Chat

```python
def chat_with_ai(request: ChatRequest) -> ChatResponse:
    # 1. Prepara conversazione con prompt di sistema
    messages = [...]

    # 2. Chiama OpenAI con capacità tool
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        tools=[RAG_TOOL],
        tool_choice="auto"
    )

    # 3. Gestisce chiamate tool
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "search_documents":
                # Esegue ricerca RAG
                chunks = rag_system.query(query)
                function_result = search_documents(query)

                # Continua conversazione con risultati
                messages.append(...)  # Chiamata tool
                messages.append(...)  # Risultato tool

                # Ottiene risposta finale
                final_response = client.chat.completions.create(...)

    return ChatResponse(...)
```

## Decisioni Chiave di Design

### 1. RAG Basato su Tool vs Sempre Attivo

**Scelto: Basato su Tool**
- ✅ L'AI decide quando RAG è necessario
- ✅ Evita ricerche irrilevanti (es. "Che tempo fa?")
- ✅ Flusso conversazionale più naturale
- ❌ Richiede buon tuning del prompt di sistema

**Alternativa: Sempre Attivo**
- ✅ Implementazione più semplice
- ❌ Chiamate API non necessarie per domande non correlate
- ❌ Potenziale confusione nelle risposte

### 2. Strategia di Chunking

**Scelto: RecursiveCharacterTextSplitter con sovrapposizione**
- ✅ Preserva contesto tra confini dei chunk
- ✅ Dimensione chunk e sovrapposizione configurabili
- ✅ Buono per documenti di testo generale
- ❌ Può dividere frasi in modo maldestro

**Parametri:**
- Dimensione chunk: 1000 caratteri (equilibrio tra contesto e precisione)
- Sovrapposizione: 200 caratteri (20% di sovrapposizione preserva contesto)

### 3. Modello di Embedding

**Scelto: text-embedding-3-small**
- ✅ 5x più economico di text-embedding-ada-002
- ✅ Migliori prestazioni sui benchmark
- ✅ Configurabile tramite variabili d'ambiente
- ❌ Modello più nuovo (meno testato in produzione)

### 4. Database Vettoriale

**Scelto: ChromaDB**
- ✅ Locale, nessuna dipendenza esterna
- ✅ API semplice perfetta per imparare
- ✅ Archiviazione persistente
- ❌ Non adatto per produzione ad alta scala

**Alternative considerate:**
- Pinecone: Basato su cloud, scalabile, ma richiede account
- Weaviate: Self-hosted, ricco di funzionalità, ma configurazione complessa
- FAISS: Veloce, ma nessun layer di persistenza

## Argomenti Avanzati

### 1. Utilizzo di Provider LLM Alternativi

Il sistema supporta qualsiasi API compatibile con OpenAI attraverso la configurazione:

**Ollama (LLM Locali):**
```bash
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.1  # o llama3, mistral, ecc.
OPENAI_API_KEY=ollama  # Può essere qualsiasi valore
```

**Altri Provider:**
```bash
# Azure OpenAI
OPENAI_BASE_URL=https://your-resource.openai.azure.com/
LLM_MODEL=gpt-4.1

# Anthropic via proxy
OPENAI_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL=claude-3-sonnet

# Deployment locale (vLLM, ecc.)
OPENAI_BASE_URL=http://localhost:8000/v1
LLM_MODEL=your-local-model
```

**Considerazioni importanti:**
- Il supporto per chiamate di funzione varia per provider
- Alcuni modelli potrebbero necessitare prompt di sistema regolati
- I modelli di embedding richiedono ancora API OpenAI per ora

### 2. Migliorare la Qualità del Recupero

**Tecniche non implementate ma da considerare:**

1. **Ricerca Ibrida**: Combina ricerca semantica (embedding) e lessicale (parole chiave)
2. **Re-ranking**: Usa un modello separato per ri-ordinare i chunk recuperati
3. **Espansione Query**: Espande le query utente con sinonimi/termini correlati
4. **Filtraggio Metadati**: Filtra per tipo documento, data, ecc.

### 3. Considerazioni di Scalabilità

**Limitazioni attuali e soluzioni:**

1. **Uso Memoria**: Caricamento di tutti gli embedding in memoria
   - Soluzione: Usa streaming o paginazione
2. **Utenti Concorrenti**: Singola istanza ChromaDB
   - Soluzione: Connection pooling o DB vettoriale distribuito
3. **Aggiornamenti Documenti**: Ricostruzione completa agli aggiornamenti
   - Soluzione: Aggiornamenti incrementali con versioning documenti

### 4. Valutazione e Monitoraggio

**Metriche da tracciare in produzione:**

1. **Metriche di Recupero**:
   - Precision@K: Chunk rilevanti nei primi K risultati
   - Recall: Frazione di chunk rilevanti recuperati
   - MRR (Mean Reciprocal Rank): Qualità del ranking

2. **Metriche End-to-End**:
   - Valutazioni soddisfazione utente
   - Tassi completamento task
   - Punteggi rilevanza risposte

3. **Metriche di Sistema**:
   - Latenza query
   - Tempo generazione embedding
   - Prestazioni ricerca vettoriale

### 5. Considerazioni di Sicurezza

**Importante per produzione:**

1. **Gestione Chiavi API**: Usa gestione sicura dei segreti
2. **Validazione Input**: Sanifica input utente
3. **Rate Limiting**: Previene abuso dell'API OpenAI
4. **Privacy Dati**: Considera LLM locali per dati sensibili

## Riferimento Configurazione

### Variabili d'Ambiente

```bash
# Configurazione LLM
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=                        # Lascia vuoto per OpenAI, imposta per altri provider
LLM_MODEL=gpt-4.1-mini                  # Modello linguistico da usare

# Configurazione Embedding
EMBEDDING_MODEL=text-embedding-3-small  # Modello embedding per ricerca vettoriale

# Configurazione RAG
CHUNK_SIZE=1000          # Caratteri per chunk
CHUNK_OVERLAP=200        # Sovrapposizione caratteri tra chunk
TOP_K_RESULTS=5          # Numero chunk da recuperare
```

### Parametri di Tuning

1. **Dimensione Chunk**:
   - Più piccola (500): Più precisa, può perdere contesto
   - Più grande (2000): Più contesto, può essere meno precisa

2. **Sovrapposizione**:
   - 10-20% della dimensione chunk è tipico
   - Più sovrapposizione = migliore preservazione contesto

3. **Risultati Top-K**:
   - Più risultati = più contesto ma anche più rumore
   - 3-7 è tipicamente ottimale

## Problemi Comuni e Soluzioni

### 1. Qualità Recupero Scarsa

**Sintomi**: Chunk irrilevanti restituiti

**Soluzioni**:
- Regola dimensione chunk e sovrapposizione
- Migliora pre-elaborazione documenti
- Prova modelli embedding diversi
- Aggiungi pre-elaborazione query

### 2. Prestazioni Lente

**Sintomi**: Tempi di risposta lunghi

**Soluzioni**:
- Riduci risultati Top-K
- Ottimizza configurazione database vettoriale
- Cache query frequenti
- Usa elaborazione asincrona

### 3. RAG Non Si Attiva

**Sintomi**: L'AI non usa il tool di ricerca

**Soluzioni**:
- Migliora prompt di sistema
- Aggiungi esempi nel few-shot prompting
- Abbassa soglia uso tool
- Rendi descrizione tool più specifica

Questa documentazione tecnica fornisce le basi per comprendere ed estendere l'implementazione RAG. Ogni componente può essere modificato e migliorato basandosi su casi d'uso specifici e requisiti.