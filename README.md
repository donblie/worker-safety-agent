# 工友安全守护Agent 🛡️

建筑工地安全智能助手 —— 安全知识随时问 · 隐患拍照能识别 · 培训内容自动生成 · 紧急情况有指导

## 功能模块

| 模块 | 说明 |
|------|------|
| 💬 安全知识问答 | 基于安全规范知识库的RAG智能问答 |
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
python init_kb.py

# 4. 启动应用
streamlit run app.py
```

## 技术架构

- **前端**: Streamlit（移动端自适应）
- **文本模型**: DeepSeek API（deepseek-chat）
- **视觉模型**: Qwen-VL（qwen-vl-max）
- **检索**: TF-IDF + 余弦相似度（scikit-learn）
- **知识库**: 建筑安全规范文档，18个文本块

## 竞赛信息

第一届海之子杯AI智能体挑战计划参赛作品
