"""
FinanceGPT Agent - Streamlit 可视化界面
运行方式：streamlit run app.py
"""

import streamlit as st
from agent import create_finance_agent

# ─── 页面配置 ───
st.set_page_config(
    page_title="FinanceGPT Agent",
    page_icon="💹",
    layout="centered",
)

st.title("💹 FinanceGPT Agent")
st.caption("AI 驱动的财经分析助手 · 支持美股 / 港股 / A股")

# ─── 示例问题 ───
with st.expander("💡 示例问题（点击展开）"):
    examples = [
        "苹果公司（AAPL）今天股价怎么样？",
        "分析腾讯（0700.HK）近30天的走势",
        "对比 AAPL、GOOGL、MSFT 三只股票",
        "茅台（600519.SS）最近表现如何？",
        "帮我分析英伟达的基本面",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state.pending_input = ex

# ─── Agent 初始化（缓存，避免重复创建） ───
@st.cache_resource
def get_agent():
    return create_finance_agent()

agent = get_agent()

# ─── 对话历史 ───
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── 侧边栏 ───
with st.sidebar:
    st.header("⚙️ 设置")
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        agent.memory.clear()
        st.rerun()

    st.divider()
    st.markdown("**技术架构**")
    st.markdown("""
- 🔗 LangChain Agent
- 📊 yfinance 行情数据  
- 🧠 GPT-4o-mini
- 💬 对话记忆（近6轮）
    """)

    st.divider()
    st.caption("⚠️ 本工具仅供学习研究，不构成投资建议")

# ─── 处理示例问题点击 ───
pending = st.session_state.pop("pending_input", None)

# ─── 输入框 ───
user_input = st.chat_input("输入你的问题，例如：帮我分析苹果股票...") or pending

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("分析中..."):
            try:
                response = agent.invoke({"input": user_input})
                answer = response["output"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                err = f"⚠️ 出错了：{str(e)}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
