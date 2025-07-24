# 技術ドキュメント: RAGデモ実装

このドキュメントはRAG（Retrieval Augmented Generation）システムの実装について詳細な技術解説を提供します。ウェブ開発は理解しているがRAGの概念は初心者のPython開発者を対象としています。

## 目次
1. [アーキテクチャ概要](#アーキテクチャ概要)
2. [RAGシステムの説明](#ragシステムの説明)
3. [実装詳細](#実装詳細)
4. [コードウォークスルー](#コードウォークスルー)
5. [主要設計決定](#主要設計決定)
6. [高度なトピック](#高度なトピック)

## アーキテクチャ概要

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   フロントエンド   │    │   FastAPI       │    │   OpenAI API    │
│   (HTML/CSS/JS) │◄──►│   バックエンド     │◄──►│   (GPT-4.1 Mini)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   RAGシステム    │◄──►│   ChromaDB      │
                       │   (rag.py)      │    │   (ベクトルDB)   │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ドキュメント    │
                       │   (.txtファイル) │
                       └─────────────────┘
```

## RAGシステムの説明

### RAGとは？

RAG（Retrieval Augmented Generation）は、外部知識へのアクセスを与えることで大規模言語モデル（LLM）を強化する技術です。学習データのみに依存する代わりに、モデルは知識ベースから関連情報を「検索」して応答を「拡張」できます。

### 我々のRAGの動作原理

1. **ドキュメント処理**: テキストドキュメントをチャンクに分割し、ベクトル埋め込みに変換
2. **保存**: 埋め込みをChromaDB（ベクトルデータベース）に保存
3. **クエリ時**: ユーザーの質問を埋め込みに変換し、保存されたチャンクとマッチング
4. **検索**: 最も類似したチャンクを検索し、LLMに提供
5. **生成**: LLMは学習データと検索されたコンテキストの両方を使用して応答を生成

## 実装詳細

### コアコンポーネント

#### 1. ドキュメント処理（`rag.py`）

```python
# コンテキスト保持のためのオーバーラップ付きテキスト分割
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=self.chunk_size,      # デフォルト: 1000文字
    chunk_overlap=self.chunk_overlap, # デフォルト: 200文字
    length_function=len,
)
```

**なぜチャンク化？**
- LLMにはトークン制限がある
- 小さなチャンクは検索精度を向上させる
- オーバーラップは境界を超えたコンテキストを保持

#### 2. ベクトル埋め込み

```python
# OpenAIの最新埋め込みモデルを使用
self.embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
)
```

**なぜ埋め込み？**
- テキストを数値ベクトルに変換
- 意味的類似性検索を可能にする
- 「機械学習」と「AIアルゴリズム」は類似した埋め込みを持つ

#### 3. ベクトルデータベース（ChromaDB）

```python
# 永続的ローカルストレージ
self.client = chromadb.PersistentClient(path="./chroma_db")
self.collection = self.client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # テキスト用コサイン類似度
)
```

**なぜChromaDB？**
- HNSWインデックスによる高速類似性検索
- 永続ストレージ（再起動後も保持）
- 教育目的に適したシンプルなAPI

#### 4. ツールベースRAG統合（`chat.py`）

```python
# OpenAI関数呼び出し定義
RAG_TOOL = {
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": "ドキュメント知識ベースを検索",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "関連ドキュメントを見つけるための検索クエリ"
                }
            },
            "required": ["query"]
        }
    }
}
```

**なぜ関数呼び出し？**
- AIがRAGを使用するタイミングを決定
- 会話フローとの自然な統合
- 関連のない質問での不要な検索を回避

## コードウォークスルー

### 1. ドキュメント取り込みプロセス

```python
def add_documents(self, documents_dir: str = "documents"):
    # 1. 既存ドキュメントをクリア
    all_items = self.collection.get()
    if all_items['ids']:
        self.collection.delete(ids=all_items['ids'])

    # 2. 各.txtファイルを処理
    for filename in os.listdir(documents_dir):
        if filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # 3. チャンクに分割
            chunks = self.text_splitter.split_text(content)

            # 4. 各チャンクのメタデータを作成
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "filename": filename,
                    "chunk_index": i
                })

    # 5. 埋め込みを生成して保存
    embeddings = self.embeddings.embed_documents(all_chunks)
    self.collection.add(
        embeddings=embeddings,
        documents=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids
    )
```

### 2. クエリプロセス

```python
def query(self, query: str, top_k: int = None) -> List[RAGChunk]:
    # 1. クエリを埋め込みに変換
    query_embedding = self.embeddings.embed_query(query)

    # 2. 類似ベクトルを検索
    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k or self.top_k
    )

    # 3. 結果を構造化形式に変換
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

### 3. チャット統合

```python
def chat_with_ai(request: ChatRequest) -> ChatResponse:
    # 1. システムプロンプトと会話を準備
    messages = [...]

    # 2. ツール機能付きでOpenAIを呼び出し
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        tools=[RAG_TOOL],
        tool_choice="auto"
    )

    # 3. ツール呼び出しを処理
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "search_documents":
                # RAG検索を実行
                chunks = rag_system.query(query)
                function_result = search_documents(query)

                # 結果と共に会話を継続
                messages.append(...)  # ツール呼び出し
                messages.append(...)  # ツール結果

                # 最終応答を取得
                final_response = client.chat.completions.create(...)

    return ChatResponse(...)
```

## 主要設計決定

### 1. ツールベース vs 常時オンRAG

**選択: ツールベース**
- ✅ AIがRAGが必要なタイミングを決定
- ✅ 関連のない検索を回避（例：「天気は？」）
- ✅ より自然な会話フロー
- ❌ 良いシステムプロンプト調整が必要

**代替案: 常時オン**
- ✅ より単純な実装
- ❌ 関連のない質問での不要なAPI呼び出し
- ❌ 応答の混乱の可能性

### 2. チャンク化戦略

**選択: オーバーラップ付きRecursiveCharacterTextSplitter**
- ✅ チャンク境界を超えたコンテキストを保持
- ✅ 設定可能なチャンクサイズとオーバーラップ
- ✅ 一般的なテキストドキュメントに適している
- ❌ 文を不自然に分割する可能性

**パラメータ:**
- チャンクサイズ: 1000文字（コンテキストと精度のバランス）
- オーバーラップ: 200文字（20%のオーバーラップでコンテキスト保持）

### 3. 埋め込みモデル

**選択: text-embedding-3-small**
- ✅ text-embedding-ada-002より5倍安価
- ✅ ベンチマークでより良い性能
- ✅ 環境変数で設定可能
- ❌ 新しいモデル（本番での実績が少ない）

### 4. ベクトルデータベース

**選択: ChromaDB**
- ✅ ローカル、外部依存なし
- ✅ 学習に最適なシンプルAPI
- ✅ 永続ストレージ
- ❌ 大規模本番には不向き

**検討した代替案:**
- Pinecone: クラウドベース、スケーラブル、ただしアカウント必要
- Weaviate: セルフホスト、機能豊富、ただし複雑なセットアップ
- FAISS: 高速、ただし永続化層なし

## 高度なトピック

### 1. 代替LLMプロバイダーの使用

システムは設定を通じてOpenAI互換のAPIをサポートします：

**Ollama（ローカルLLM）:**
```bash
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.1  # または llama3, mistral など
OPENAI_API_KEY=ollama  # 任意の値
```

**その他のプロバイダー:**
```bash
# Azure OpenAI
OPENAI_BASE_URL=https://your-resource.openai.azure.com/
LLM_MODEL=gpt-4.1

# プロキシ経由のAnthropic
OPENAI_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL=claude-3-sonnet

# ローカル展開（vLLMなど）
OPENAI_BASE_URL=http://localhost:8000/v1
LLM_MODEL=your-local-model
```

**重要な考慮事項:**
- 関数呼び出しサポートはプロバイダーによって異なる
- 一部のモデルはシステムプロンプトの調整が必要
- 埋め込みモデルは現在OpenAI APIが必要

### 2. 検索品質の向上

**実装されていないが検討価値のある技術:**

1. **ハイブリッド検索**: 意味的（埋め込み）検索と語彙的（キーワード）検索の組み合わせ
2. **再ランク付け**: 検索されたチャンクを再ランク付けする別モデルの使用
3. **クエリ拡張**: 同義語/関連語でユーザークエリを拡張
4. **メタデータフィルタリング**: ドキュメントタイプ、日付等でフィルタリング

### 2. スケーリング考慮事項

**現在の制限と解決策:**

1. **メモリ使用量**: すべての埋め込みをメモリに読み込み
   - 解決策: ストリーミングまたはページネーションの使用
2. **同時ユーザー**: 単一ChromaDBインスタンス
   - 解決策: コネクションプーリングまたは分散ベクトルDB
3. **ドキュメント更新**: 更新時の完全再構築
   - 解決策: ドキュメントバージョニング付き増分更新

### 3. 評価と監視

**本番で追跡すべきメトリクス:**

1. **検索メトリクス**:
   - Precision@K: トップK結果の関連チャンク
   - Recall: 検索された関連チャンクの割合
   - MRR（平均逆順位）: ランキング品質

2. **エンドツーエンドメトリクス**:
   - ユーザー満足度評価
   - タスク完了率
   - 応答関連性スコア

3. **システムメトリクス**:
   - クエリレイテンシ
   - 埋め込み生成時間
   - ベクトル検索性能

### 4. セキュリティ考慮事項

**本番で重要:**

1. **APIキー管理**: セキュアなシークレット管理の使用
2. **入力検証**: ユーザー入力のサニタイズ
3. **レート制限**: OpenAI API乱用の防止
4. **データプライバシー**: 機密データにはローカルLLMを検討

## 設定リファレンス

### 環境変数

```bash
# LLM設定
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=                        # OpenAIの場合は空、他のプロバイダーの場合は設定
LLM_MODEL=gpt-4.1-mini                  # 使用する言語モデル

# 埋め込み設定
EMBEDDING_MODEL=text-embedding-3-small  # ベクトル検索用埋め込みモデル

# RAG設定
CHUNK_SIZE=1000          # チャンクあたりの文字数
CHUNK_OVERLAP=200        # チャンク間の文字オーバーラップ
TOP_K_RESULTS=5          # 検索するチャンク数
```

### チューニングパラメータ

1. **チャンクサイズ**:
   - 小さい（500）: より精密、コンテキスト不足の可能性
   - 大きい（2000）: より多くのコンテキスト、精度低下の可能性

2. **オーバーラップ**:
   - チャンクサイズの10-20%が一般的
   - より多くのオーバーラップ = より良いコンテキスト保持

3. **トップK結果**:
   - より多い結果 = より多くのコンテキストだがノイズも増加
   - 3-7が一般的に最適

## 一般的な問題と解決策

### 1. 検索品質不良

**症状**: 関連性のないチャンクが返される

**解決策**:
- チャンクサイズとオーバーラップを調整
- ドキュメント前処理を改善
- 異なる埋め込みモデルを試す
- クエリ前処理を追加

### 2. 性能低下

**症状**: 応答時間が長い

**解決策**:
- トップK結果を削減
- ベクトルデータベースconfig最適化
- 頻繁なクエリのキャッシュ
- 非同期処理の使用

### 3. RAGがトリガーされない

**症状**: AIが検索ツールを使用しない

**解決策**:
- システムプロンプトを改善
- few-shotプロンプティングで例を追加
- ツール使用閾値を下げる
- ツール説明をより具体的にする

この技術ドキュメントは、RAG実装の理解と拡張の基盤を提供します。各コンポーネントは、特定のユースケースと要件に基づいて修正・改善できます。
