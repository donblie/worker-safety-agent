"""
知识库初始化脚本
运行一次即可将安全规范文档加载到本地知识库（TF-IDF 关键词检索，预留 BGE 语义嵌入接口）

用法: python init_kb.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.knowledge_base import get_knowledge_base


def main():
    print("=" * 50)
    print("  工友安全守护Agent — 知识库初始化")
    print("=" * 50)
    print()

    # 初始化知识库
    kb = get_knowledge_base()

    # 加载文档
    print("[...] Loading safety regulation documents...")
    print()
    count = kb.load_documents()
    print()

    if count > 0:
        print("=" * 50)
        print(f"  [OK] Knowledge base initialized! {count} chunks total")
        print(f"  [PATH] Cache: {kb.get_stats()['cache_file']}")
        print()
        print("  现在可以启动应用了:")
        print("  streamlit run app.py")
        print("=" * 50)
    else:
        print("=" * 50)
        print("  [WARN] No documents loaded")
        print(f"  请检查文档目录: {os.path.abspath('./data/regulations')}")
        print("=" * 50)


if __name__ == "__main__":
    main()
