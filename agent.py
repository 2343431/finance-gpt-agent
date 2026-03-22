"""
FinanceGPT Agent - 财经问答 AI Agent
使用 LangChain + Alpha Vantage + Claude Opus 构建
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()

AV_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# ─────────────────────────────────────────
# Tools 定义
# ─────────────────────────────────────────

@tool
def get_stock_price(ticker: str) -> str:
    """
    查询股票的实时价格和基本信息。
    ticker: 股票代码，如 AAPL（苹果）、GOOGL（谷歌）、TSLA（特斯拉）
    """
    try:
        r = requests.get(BASE_URL, params={
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": AV_KEY,
        }, timeout=10)
        data = r.json().get("Global Quote", {})

        if not data:
            return f"未找到股票 {ticker} 的数据，请检查股票代码。"

        result = {
            "ticker": ticker,
            "current_price": data.get("05. price"),
            "change": data.get("09. change"),
            "change_pct": data.get("10. change percent"),
            "volume": data.get("06. volume"),
            "latest_trading_day": data.get("07. latest trading day"),
            "previous_close": data.get("08. previous close"),
            "open": data.get("02. open"),
            "high": data.get("03. high"),
            "low": data.get("04. low"),
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"查询股票 {ticker} 时出错：{str(e)}"


@tool
def get_stock_history(ticker: str, days: int = 30) -> str:
    """
    获取股票历史价格走势，用于趋势分析。
    ticker: 股票代码
    days: 查询天数，默认30天
    """
    try:
        r = requests.get(BASE_URL, params={
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "compact",
            "apikey": AV_KEY,
        }, timeout=10)
        data = r.json().get("Time Series (Daily)", {})

        if not data:
            return f"未找到股票 {ticker} 的历史数据。"

        dates = sorted(data.keys(), reverse=True)[:days]
        closes = [float(data[d]["4. close"]) for d in dates]

        start_price = closes[-1]
        end_price = closes[0]
        total_return = (end_price - start_price) / start_price * 100

        ma5 = sum(closes[:5]) / 5 if len(closes) >= 5 else None
        ma20 = sum(closes[:20]) / 20 if len(closes) >= 20 else None

        result = {
            "ticker": ticker,
            "period": f"{len(dates)}天",
            "start_price": round(start_price, 2),
            "end_price": round(end_price, 2),
            "total_return_pct": round(total_return, 2),
            "max_price": round(max(closes), 2),
            "min_price": round(min(closes), 2),
            "ma5": round(ma5, 2) if ma5 else "数据不足",
            "ma20": round(ma20, 2) if ma20 else "数据不足",
            "trend": "上涨" if total_return > 0 else "下跌",
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"查询历史数据时出错：{str(e)}"


@tool
def compare_stocks(tickers: str) -> str:
    """
    对比多只股票的实时表现。
    tickers: 用逗号分隔的股票代码，如 "AAPL,GOOGL,MSFT"
    """
    try:
        ticker_list = [t.strip() for t in tickers.split(",")]
        results = []

        for ticker in ticker_list[:3]:  # 免费版限速，最多3只
            r = requests.get(BASE_URL, params={
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": AV_KEY,
            }, timeout=10)
            data = r.json().get("Global Quote", {})
            if not data:
                continue
            results.append({
                "ticker": ticker,
                "current_price": data.get("05. price"),
                "change_pct": data.get("10. change percent"),
                "volume": data.get("06. volume"),
            })

        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"对比股票时出错：{str(e)}"


# ─────────────────────────────────────────
# Agent 初始化
# ─────────────────────────────────────────

def create_finance_agent():
    llm = ChatOpenAI(
        model="claude-opus-4-5-20251101",
        temperature=0,
        openai_api_key=os.getenv("AIIONLY_API_KEY"),
        base_url="https://api.aiionly.com/v1",
    )

    tools = [get_stock_price, get_stock_history, compare_stocks]

    system_prompt = f"""你是一位专业的财经分析助手，擅长分析股票行情、解读市场趋势。

你的能力：
- 查询实时股票价格（当日开盘、最高、最低、收盘、涨跌幅）
- 分析股票历史走势（MA5/MA20均线、涨跌幅）
- 对比多只股票的表现（每次最多3只）

回答规范：
1. 先调用工具获取数据，再进行分析，不要凭空捏造数据
2. 分析时结合具体数字，给出有根据的判断
3. 适当提示投资风险
4. 使用简洁专业的中文回答

注意：只支持美股代码，如 AAPL、GOOGL、TSLA、MSFT、NVDA 等

当前日期：{datetime.now().strftime("%Y年%m月%d日")}"""

    agent = create_react_agent(llm, tools, prompt=system_prompt)
    return agent


# ─────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────

def main():
    print("=" * 50)
    print("  FinanceGPT Agent 🤖💹")
    print("  输入 'quit' 退出")
    print("=" * 50)

    agent = create_finance_agent()
    chat_history = []

    examples = [
        "苹果公司（AAPL）今天股价怎么样？",
        "帮我分析英伟达（NVDA）近30天的走势",
        "对比一下 AAPL、GOOGL、MSFT 这三只股票",
    ]
    print("\n💡 示例问题：")
    for q in examples:
        print(f"   • {q}")
    print()

    while True:
        try:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "退出"):
                print("再见！")
                break

            chat_history.append(HumanMessage(content=user_input))
            print("\n分析中...\n")

            result = agent.invoke({"messages": chat_history})
            response = result["messages"][-1].content

            chat_history.append(AIMessage(content=response))
            print(f"助手: {response}\n")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"出错了：{e}\n")


if __name__ == "__main__":
    main()
