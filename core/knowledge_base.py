"""
知识库模块 —— TF-IDF 关键词检索（默认），预留 BGE 语义检索升级接口
- 文档加载、分块、向量索引
- TF-IDF 关键词检索（零依赖、毫秒级、云端稳定）；BGE 语义嵌入为可选升级
- 搜索：输入自然语言问题，返回最相关的规范段落
"""
import os
import re
import pickle
import threading
import numpy as np
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity

from utils.config import (
    REGULATIONS_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_TOP_K,
    RETRIEVAL_MIN_SCORE,
    KB_EMBEDDING_MODEL,
    KB_CACHE_DIR,
)
from utils.logger import log, log_retrieval

# ── 延迟加载 BGE（可选依赖）────────────────────
_SENTENCE_TRANSFORMERS_AVAILABLE = False
_SentenceTransformer = None

def _try_load_sentence_transformers():
    """尝试加载 sentence-transformers，失败则保持 False"""
    global _SENTENCE_TRANSFORMERS_AVAILABLE, _SentenceTransformer
    if _SentenceTransformer is not None:
        return
    try:
        from sentence_transformers import SentenceTransformer as ST
        _SentenceTransformer = ST
        _SENTENCE_TRANSFORMERS_AVAILABLE = True
    except ImportError:
        _SENTENCE_TRANSFORMERS_AVAILABLE = False
        log("INFO", "sentence-transformers not installed, using TF-IDF fallback")


class KnowledgeBase:
    """建筑安全规范知识库（TF-IDF 关键词检索，预留 BGE 语义检索接口）"""

    CACHE_VERSION = 2  # 缓存版本号，升级格式时递增

    def __init__(self):
        self.chunks: List[Dict] = []           # 所有文本块
        self.embedder = None                   # BGE 模型（SentenceTransformer）
        self.embedder_model: str = ""          # 使用的嵌入模型名
        self.vectorizer = None                 # TF-IDF vectorizer（默认检索）
        self.chunk_vectors = None              # 向量矩阵（numpy array 或 scipy sparse）
        self._use_embeddings = False           # 是否使用 BGE 语义检索
        self.cache_file = os.path.join(KB_CACHE_DIR, "kb_cache.pkl")
        if not self._load_cache():
            # 缓存不存在/无效/环境不匹配（如本地BGE缓存、云端无BGE）→ 自动从原始文档重建
            log("INFO", "Cache not usable, auto-rebuilding knowledge base from documents...")
            self.load_documents()

    # ── 文档分块 ────────────────────────────────

    def _split_text(self, text: str, doc_name: str) -> List[Dict]:
        """将长文本切成带重叠的小块"""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) > CHUNK_SIZE and current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "doc_name": doc_name,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1
                if len(current_chunk) > CHUNK_OVERLAP:
                    current_chunk = current_chunk[-CHUNK_OVERLAP:] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "doc_name": doc_name,
                "chunk_index": chunk_index,
            })

        return chunks

    # ── 缓存管理 ────────────────────────────────

    def _load_cache(self):
        """从磁盘加载已缓存的向量化数据"""
        if not os.path.exists(self.cache_file):
            log("INFO", f"Cache file not found ({self.cache_file}), KB not initialized. Run: python init_kb.py")
            return False

        try:
            with open(self.cache_file, "rb") as f:
                data = pickle.load(f)

            cache_version = data.get("_version", 1)

            self.chunks = data.get("chunks", [])
            if not self.chunks:
                return False

            # 检查 BGE 是否可用
            _try_load_sentence_transformers()

            # 版本2+ 使用 BGE 嵌入
            if cache_version >= 2 and _SENTENCE_TRANSFORMERS_AVAILABLE:
                cached_model = data.get("embedder_model", "")
                target_model = KB_EMBEDDING_MODEL

                if cached_model == target_model:
                    self.embedder_model = cached_model
                    self.chunk_vectors = data.get("chunk_vectors")
                    self.vectorizer = None
                    self._use_embeddings = True
                    log("INFO", f"Loaded {len(self.chunks)} chunks (BGE: {cached_model})")
                    return True
                else:
                    log("INFO", f"Embedding model changed ({cached_model} -> {target_model}), "
                        "will rebuild index")

            # 版本1 或 BGE不可用：使用 TF-IDF
            if not self._use_embeddings:
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.vectorizer = data.get("vectorizer")
                self.chunk_vectors = data.get("chunk_vectors")
                if self.chunks and self.vectorizer is not None:
                    log("INFO", f"Loaded {len(self.chunks)} chunks (TF-IDF, "
                        f"vocab: {len(self.vectorizer.vocabulary_)} tokens)")
                    return True

            return False

        except Exception as e:
            log("WARN", f"Cache load failed: {e}")
            return False

    def _save_cache(self):
        """保存向量化数据到磁盘"""
        os.makedirs(KB_CACHE_DIR, exist_ok=True)
        cache_data = {
            "_version": self.CACHE_VERSION,
            "chunks": self.chunks,
            "chunk_vectors": self.chunk_vectors,
        }
        if self._use_embeddings:
            cache_data["embedder_model"] = self.embedder_model
            cache_data["vectorizer"] = None
        else:
            cache_data["vectorizer"] = self.vectorizer
            cache_data["embedder_model"] = ""

        with open(self.cache_file, "wb") as f:
            pickle.dump(cache_data, f)

    # ── 文档加载与索引 ──────────────────────────

    def load_documents(self, docs_dir: str = None) -> int:
        """
        加载目录中的所有txt/md文档，分块并建立索引。
        TF-IDF 关键词检索（默认）；已安装 BGE 时自动切换为语义检索（可选升级）。
        返回：已加载的chunk数量
        """
        docs_dir = docs_dir or REGULATIONS_DIR
        if not os.path.exists(docs_dir):
            log("WARN", f"Document directory not found: {docs_dir}")
            return 0

        all_chunks = []
        for filename in sorted(os.listdir(docs_dir)):
            if filename.endswith((".txt", ".md")):
                filepath = os.path.join(docs_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()

                if not text.strip():
                    continue

                chunks = self._split_text(text, filename)
                all_chunks.extend(chunks)
                print(f"  [FILE] {filename}: {len(chunks)} chunks")

        if not all_chunks:
            log("WARN", "No documents found")
            return 0

        self.chunks = all_chunks
        contents = [c["content"] for c in all_chunks]

        # 可选：已安装 BGE 时使用语义嵌入
        _try_load_sentence_transformers()
        if _SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                model_name = KB_EMBEDDING_MODEL
                print(f"[...] Loading BGE embedding model: {model_name} ...")
                self.embedder = _SentenceTransformer(model_name)
                print(f"[...] Encoding {len(contents)} chunks ...")
                self.chunk_vectors = self.embedder.encode(
                    contents,
                    normalize_embeddings=True,  # L2归一化，cosine = dot product
                    show_progress_bar=True,
                )
                self.embedder_model = model_name
                self.vectorizer = None
                self._use_embeddings = True
                print(f"[OK] BGE embeddings built! dim={self.chunk_vectors.shape[1]}")
            except Exception as e:
                log("ERROR", f"BGE encoding failed: {e}, falling back to TF-IDF")
                self._use_embeddings = False
                self.embedder = None

        # 默认：使用 TF-IDF 关键词检索
        if not self._use_embeddings:
            from sklearn.feature_extraction.text import TfidfVectorizer
            print(f"[...] Building TF-IDF index for {len(all_chunks)} chunks ...")
            self.vectorizer = TfidfVectorizer(
                analyzer="char",
                ngram_range=(1, 2),
                max_df=0.9,
                min_df=1,
                max_features=10000,
            )
            self.chunk_vectors = self.vectorizer.fit_transform(contents)
            print(f"[OK] TF-IDF index built! vocab: {len(self.vectorizer.vocabulary_)} tokens")

        # 保存缓存
        self._save_cache()
        mode = "BGE" if self._use_embeddings else "TF-IDF"
        print(f"[OK] Knowledge base ready! Total: {len(all_chunks)} chunks, mode: {mode}")
        return len(all_chunks)

    # ── 检索 ───────────────────────────────────

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        检索最相关的规范段落
        返回: [{"content": "...", "doc_name": "...", "score": 0.xx}, ...]
        """
        import time as _time
        start = _time.perf_counter()
        top_k = top_k or RETRIEVAL_TOP_K

        if not self.chunks:
            log_retrieval(query, 0, 0.0, (_time.perf_counter() - start) * 1000)
            return []

        # 查询向量化
        if self._use_embeddings and self.embedder is not None:
            query_vec = self.embedder.encode(
                [query], normalize_embeddings=True
            )
            # BGE 已 L2 归一化，dot product = cosine similarity
            scores = np.dot(query_vec, self.chunk_vectors.T)[0]
        elif self.vectorizer is not None:
            query_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self.chunk_vectors)[0]
        else:
            log_retrieval(query, 0, 0.0, (_time.perf_counter() - start) * 1000)
            return []

        # 取top-k，过滤低于阈值的噪音
        top_indices = scores.argsort()[-top_k:][::-1]

        formatted = []
        for idx in top_indices:
            if float(scores[idx]) >= RETRIEVAL_MIN_SCORE:
                chunk = self.chunks[idx]
                formatted.append({
                    "content": chunk["content"],
                    "doc_name": chunk["doc_name"],
                    "chunk_index": chunk["chunk_index"],
                    "score": round(float(scores[idx]), 4),
                })

        elapsed = (_time.perf_counter() - start) * 1000
        top_score = formatted[0]["score"] if formatted else 0.0
        log_retrieval(query, len(formatted), top_score, elapsed)

        return formatted

    def search_formatted(self, query: str, top_k: int = None) -> str:
        """检索并格式化为带编号的文本，方便注入LLM上下文"""
        results = self.search(query, top_k)
        if not results:
            return ""

        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[参考资料 {i}] 来源: {r['doc_name']} (相关度: {r['score']:.2f})")
            lines.append(r["content"])
            lines.append("")

        return "\n".join(lines)

    # ── 状态查询 ───────────────────────────────

    def get_stats(self) -> Dict:
        """获取知识库统计信息"""
        return {
            "total_chunks": len(self.chunks),
            "cache_file": self.cache_file,
            "mode": "BGE" if self._use_embeddings else "TF-IDF",
            "embedding_model": self.embedder_model if self._use_embeddings else "TF-IDF (char ngram)",
        }

    def is_ready(self) -> bool:
        """知识库是否可用"""
        has_vectors = (
            (self._use_embeddings and self.chunk_vectors is not None) or
            (not self._use_embeddings and self.vectorizer is not None)
        )
        return len(self.chunks) > 0 and has_vectors


# 全局单例（线程安全）
_knowledge_base: KnowledgeBase = None
_kb_lock = threading.Lock()


def get_knowledge_base() -> KnowledgeBase:
    """获取知识库单例"""
    global _knowledge_base
    if _knowledge_base is None:
        with _kb_lock:
            if _knowledge_base is None:
                _knowledge_base = KnowledgeBase()
    return _knowledge_base
