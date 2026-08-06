"""
知识库模块 —— 基于 TF-IDF 关键词检索
- 文档加载、分块、关键词索引
- 零外部下载，纯Python实现，scikit-learn内置
- 搜索：输入自然语言问题，返回最相关的规范段落
"""
import os
import re
import pickle
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.config import (
    REGULATIONS_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_TOP_K,
    KB_CACHE_DIR,
)


class KnowledgeBase:
    """建筑安全规范知识库（TF-IDF关键词检索）"""

    def __init__(self):
        self.chunks: List[Dict] = []           # 所有文本块
        self.vectorizer: TfidfVectorizer = None
        self.chunk_vectors = None              # TF-IDF矩阵
        self.cache_file = os.path.join(KB_CACHE_DIR, "kb_cache.pkl")
        self._load_cache()

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
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    data = pickle.load(f)
                self.chunks = data.get("chunks", [])
                self.vectorizer = data.get("vectorizer")
                self.chunk_vectors = data.get("chunk_vectors")
                if self.chunks:
                    print(f"[OK] Loaded {len(self.chunks)} chunks from cache")
                return True
            except Exception as e:
                print(f"[WARN] Cache load failed: {e}")
        return False

    def _save_cache(self):
        """保存向量化数据到磁盘"""
        os.makedirs(KB_CACHE_DIR, exist_ok=True)
        with open(self.cache_file, "wb") as f:
            pickle.dump({
                "chunks": self.chunks,
                "vectorizer": self.vectorizer,
                "chunk_vectors": self.chunk_vectors,
            }, f)

    # ── 文档加载与索引 ──────────────────────────

    def load_documents(self, docs_dir: str = None) -> int:
        """
        加载目录中的所有txt/md文档，分块并建立TF-IDF索引
        返回：已加载的chunk数量
        """
        docs_dir = docs_dir or REGULATIONS_DIR
        if not os.path.exists(docs_dir):
            print(f"[WARN] Document directory not found: {docs_dir}")
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
            print("[WARN] No documents found")
            return 0

        self.chunks = all_chunks

        # 构建TF-IDF索引
        print(f"[...] Building TF-IDF index for {len(all_chunks)} chunks ...")
        contents = [c["content"] for c in all_chunks]

        # TF-IDF参数：中文用字符级ngram(1,2)，效果最好
        self.vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=(1, 2),
            max_df=0.9,
            min_df=1,
            max_features=10000,
        )
        self.chunk_vectors = self.vectorizer.fit_transform(contents)

        # 保存缓存
        self._save_cache()

        print(f"[OK] Knowledge base built! Total: {len(all_chunks)} chunks, "
              f"vocabulary: {len(self.vectorizer.vocabulary_)} tokens")
        return len(all_chunks)

    # ── 检索 ───────────────────────────────────

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        检索最相关的规范段落
        返回: [{"content": "...", "doc_name": "...", "score": 0.xx}, ...]
        """
        top_k = top_k or RETRIEVAL_TOP_K

        if not self.chunks or self.vectorizer is None:
            return []

        # 查询向量化
        query_vec = self.vectorizer.transform([query])

        # 计算余弦相似度
        scores = cosine_similarity(query_vec, self.chunk_vectors)[0]

        # 取top-k
        top_indices = scores.argsort()[-top_k:][::-1]

        formatted = []
        for idx in top_indices:
            if scores[idx] > 0:
                chunk = self.chunks[idx]
                formatted.append({
                    "content": chunk["content"],
                    "doc_name": chunk["doc_name"],
                    "chunk_index": chunk["chunk_index"],
                    "score": round(float(scores[idx]), 4),
                })

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
        }

    def is_ready(self) -> bool:
        """知识库是否可用"""
        return len(self.chunks) > 0 and self.vectorizer is not None


# 全局单例
_knowledge_base: KnowledgeBase = None


def get_knowledge_base() -> KnowledgeBase:
    """获取知识库单例"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base
