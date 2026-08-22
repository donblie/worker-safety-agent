# 工友安全守护Agent 🛡️

建筑工地安全智能助手 —— 安全知识随时问 · 隐患拍照能识别 · 培训内容自动生成 · 紧急情况有指导 · **AI Agent智能调度**

## 📱 扫码体验

<p align="center">
  <img src="docs/app_qrcode.png" width="200" alt="扫码体验工友安全守护Agent">
</p>
<p align="center"><b>👆 手机扫码直接打开（Streamlit Cloud）</b></p>

## 功能模块

| 模块 | 说明 |
|------|------|
| 🤖 **对话助手 (NEW)** | 单Agent + Function Calling统一入口，智能判断意图，自动调度工具 |
| 💬 安全知识问答 | 基于安全规范知识库的RAG智能问答，流式输出+多轮对话 |
| 📷 工地隐患识别 | AI视觉分析工地照片，识别安全隐患 |
| 📚 安全培训助手 | 15工种×15主题×3难度，自动生成培训内容 |
| 🆘 应急处理指导 | 14种紧急类型，分步骤应急指导 |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥（将.env.example复制为.env并填入密钥）
#    - DEEPSEEK_API_KEY: 从 platform.deepseek.com 获取
#    - QWEN_API_KEY: 从 dashscope.aliyun.com 获取

# 3. 初始化知识库
python scripts/init_kb.py

# 4. 启动应用
streamlit run app.py
```

## 技术架构

- **前端**: Streamlit（移动端自适应，3套主题一键切换）
- **文本模型**: DeepSeek（deepseek-chat），支持流式输出 + Function Calling
- **视觉模型**: Qwen-VL（qwen-vl-max）
- **检索**: TF-IDF关键词检索（char ngram 1-2），零外部依赖、毫秒级响应；预留BGE语义嵌入接口，知识库扩充后可无缝升级
- **Agent**: 单Agent + 4Tool（规范搜索/照片分析/培训生成/应急指导），DeepSeek Function Calling自动调度
- **工程化**: JSON Schema校验、LRU缓存+TTL、结构化日志、线程安全单例、60+安全关键词过滤
- **知识库**: 建筑安全规范文档（高处作业/脚手架/临时用电/个人防护/模板工程/塔吊起重），26个语义块

## 项目结构

```
worker-safety-agent/
├── app.py                    # 主入口（3主题系统+5功能卡片）
├── pages/
│   ├── 01_安全知识问答.py    # RAG问答（流式+上下文注入）
│   ├── 02_工地隐患识别.py    # 视觉隐患分析
│   ├── 03_安全培训助手.py    # 培训内容生成
│   ├── 04_应急处理指导.py    # 应急分步指导
│   └── 05_对话助手.py (NEW)  # Agent统一入口
├── core/
│   ├── agent.py (NEW)        # Agent调度器+Tool定义
│   ├── llm_client.py         # DeepSeek API (streaming+FC支持)
│   ├── knowledge_base.py     # TF-IDF检索知识库（预留BGE接口）
│   ├── vision_analyzer.py    # 图片分析引擎
│   ├── training_generator.py # 培训生成引擎
│   └── emergency_guide.py    # 应急指导引擎
├── utils/
│   ├── json_parser.py        # JSON提取+Schema校验
│   ├── safety_guard.py       # 全局兜底+安全过滤
│   ├── cache.py              # LRU内存缓存
│   ├── logger.py             # 结构化日志
│   ├── prompts.py            # System Prompts
│   ├── config.py             # 配置管理
│   └── ui_components.py      # UI共享组件
├── data/
│   ├── regulations/          # 安全规范文档
│   ├── emergency/            # 应急预案文档
│   └── kb_cache/             # 知识库缓存
├── requirements.txt
└── README.md
```

## 竞赛信息

第一届海之子杯AI智能体挑战计划参赛作品
