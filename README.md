# 💹 FinanceGPT Agent

> 基于 LangChain Agent 架构的 AI 财经分析助手，支持自然语言查询美股、港股、A 股行情。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)

---

## 🎯 项目背景

这个项目探索 **AI Agent 在金融信息处理场景中的应用**。传统的股票查询工具需要用户自己拼接 API、手动整理数据、再人工分析——这个 Agent 把这三个步骤全部自动化：用户只需用自然语言提问，Agent 自主决策调用哪些工具、以什么顺序执行，最终输出综合分析报告。

---

## ✨ 功能演示

**输入：** "帮我分析腾讯最近一个月的走势，并和阿里对比"

**Agent 自动执行：**
1. 调用 `get_stock_history("0700.HK", 30)` → 获取腾讯30天数据
2. 调用 `get_stock_history("9988.HK", 30)` → 获取阿里30天数据  
3. 调用 `compare_stocks("0700.HK,9988.HK")` → 对比两者表现
4. 综合数据，生成中文分析报告

---

## 🛠️ 技术架构

```
用户自然语言输入
        ↓
  LangChain Agent (ReAct 框架)
        ↓
  ┌─────────────────────────┐
  │      Tool Router        │
  └─────────────────────────┘
     ↙        ↓        ↘
get_stock  get_history  compare
 _price                 _stocks
     ↘        ↓        ↙
       yfinance API
             ↓
   GPT-4o-mini 综合分析
             ↓
      中文分析报告输出
```

**核心组件：**
- **Agent 框架**：LangChain `create_openai_tools_agent`，基于 ReAct 推理模式
- **数据源**：yfinance（免费实时行情）
- **记忆**：`ConversationBufferWindowMemory`，保留最近 6 轮对话上下文
- **前端**：Streamlit（5 分钟部署可视化界面）

---

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/finance-gpt-agent
cd finance-gpt-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

# 4a. 命令行模式
python agent.py

# 4b. 可视化界面
streamlit run app.py
```

---

## 💬 示例对话

```
你: 苹果公司最近怎么样？

Agent 思考中...
> 调用工具: get_stock_price("AAPL")
> 调用工具: get_stock_history("AAPL", 30)

助手: 苹果公司（AAPL）当前报价 $182.5，较昨日上涨 1.2%。
近30天走势来看，从 $171.3 上涨至 $182.5，涨幅约 6.5%，
整体呈上升趋势。MA5（$180.2）已突破 MA20（$176.8），
显示短期动能较强。52周高点 $199.6，当前距高点仍有约 8.5% 空间...
```

---

## 🤖 AI 如何改变我的开发工作流

这个项目的开发过程本身就是"AI 原生工作流"的实践：

| 环节 | 传统方式 | AI 辅助方式 | 效率提升 |
|------|---------|------------|---------|
| 代码框架搭建 | 查文档 + 手写样板代码 | 用 Claude 生成 LangChain Agent 骨架 | 4h → 40min |
| yfinance API 探索 | 逐个翻 API 文档 | 直接问"如何获取PE、52周高低点" | 2h → 15min |
| Bug 调试 | Stack Overflow + 反复试错 | 把报错贴给 AI，定位根因 | 30min → 5min |
| README 撰写 | 自己从零写 | AI 生成初稿，人工修改润色 | 2h → 20min |

**最大的改变是心态转变：** 遇到不熟悉的领域（如金融数据 API），不再感到焦虑，因为 AI 可以快速帮我建立"够用"的知识框架，让我专注在架构决策而非语法细节。

---

## 📈 后续计划

- [ ] 接入 Serper API，支持实时财经新闻搜索
- [ ] 添加情绪分析工具（用 LLM 分析新闻正负面）
- [ ] 支持生成价格走势图表（matplotlib）
- [ ] 接入 CrewAI，实现多 Agent 协作分析

---

## ⚠️ 免责声明

本项目仅用于技术学习和研究，不构成任何投资建议。股市有风险，投资需谨慎。

---

## 🧪 自动化评测

项目包含完整的评测脚本 `eval.py`，对 Agent 的回答质量进行系统化测试：

```bash
python3 eval.py
```

**最新评测结果：**

| 用例 ID | 测试分类 | 结果 | 响应时间 |
|---------|---------|------|---------|
| TC001 | 股价查询 | ✅ PASS | 10.96s |
| TC002 | 历史走势 | ✅ PASS | 14.9s |
| TC003 | 边界测试（无效代码） | ❌ FAIL | 9.99s |
| TC004 | 自然语言理解 | ✅ PASS | 15.77s |
| TC005 | 多步推理 | ✅ PASS | 20.24s |

**通过率：80%（4/5）｜平均响应时间：14.37s**

TC003 失败原因：Agent 对无效股票代码的回复措辞与预设关键词不匹配，已记录为待优化 case——这正是评测框架的价值所在：系统化发现 Agent 的边界问题。

**评测维度：**
- 关键词覆盖率（回答是否包含股票代码、价格数字等必要信息）
- 响应时间（是否在限定时间内完成）
- 边界值处理（错误输入是否给出合理提示）
- 自然语言理解（不给代码只说公司名，能否正确识别）
