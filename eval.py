"""
FinanceGPT Agent - 自动化评测脚本
测试 Agent 回答的质量、准确性和响应时间
"""

import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import requests

# ─────────────────────────────────────────
# 直接在 eval 里初始化 Agent（避免导入问题）
# ─────────────────────────────────────────

AV_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
AV_BASE = "https://www.alphavantage.co/query"

@tool
def get_stock_price(ticker: str) -> str:
    """查询股票实时价格。ticker: 股票代码如 AAPL"""
    try:
        r = requests.get(AV_BASE, params={
            "function": "GLOBAL_QUOTE", "symbol": ticker,
            "apikey": AV_KEY,
        }, timeout=10)
        data = r.json().get("Global Quote", {})
        if not data:
            return f"未找到股票 {ticker} 的数据"
        return json.dumps({
            "ticker": ticker,
            "current_price": data.get("05. price"),
            "change_pct": data.get("10. change percent"),
            "volume": data.get("06. volume"),
        }, ensure_ascii=False)
    except Exception as e:
        return f"查询出错：{str(e)}"

@tool
def get_stock_history(ticker: str, days: int = 30) -> str:
    """获取股票历史走势。ticker: 股票代码, days: 天数"""
    try:
        r = requests.get(AV_BASE, params={
            "function": "TIME_SERIES_DAILY", "symbol": ticker,
            "outputsize": "compact", "apikey": AV_KEY,
        }, timeout=10)
        data = r.json().get("Time Series (Daily)", {})
        if not data:
            return f"未找到股票 {ticker} 的历史数据"
        dates = sorted(data.keys(), reverse=True)[:days]
        closes = [float(data[d]["4. close"]) for d in dates]
        ret = (closes[0] - closes[-1]) / closes[-1] * 100
        return json.dumps({
            "ticker": ticker, "period": f"{len(dates)}天",
            "start_price": round(closes[-1], 2),
            "end_price": round(closes[0], 2),
            "total_return_pct": round(ret, 2),
            "trend": "上涨" if ret > 0 else "下跌",
        }, ensure_ascii=False)
    except Exception as e:
        return f"查询出错：{str(e)}"

def build_agent():
    api_key = os.getenv("AIIONLY_API_KEY", "")
    llm = ChatOpenAI(
        model="claude-opus-4-5-20251101",
        temperature=0,
        openai_api_key=api_key,
        base_url="https://api.aiionly.com/v1",
    )
    return create_react_agent(llm, [get_stock_price, get_stock_history])

# ─────────────────────────────────────────
# 测试用例
# ─────────────────────────────────────────

TEST_CASES = [
    {
        "id": "TC001", "category": "股价查询",
        "input": "苹果公司（AAPL）今天股价是多少？",
        "must_contain": ["AAPL", "$"],
        "must_not_contain": [],
        "max_response_time": 20,
    },
    {
        "id": "TC002", "category": "历史走势",
        "input": "帮我分析英伟达（NVDA）近30天的走势",
        "must_contain": ["NVDA", "%"],
        "must_not_contain": [],
        "max_response_time": 25,
    },
    {
        "id": "TC003", "category": "边界测试",
        "input": "查询一个不存在的股票代码 XYZXYZ123",
        "must_contain": ["未找到", "不存在", "无效", "检查", "无法"],
        "must_not_contain": [],
        "max_response_time": 20,
    },
    {
        "id": "TC004", "category": "自然语言理解",
        "input": "特斯拉最近怎么样？",
        "must_contain": ["TSLA", "$"],
        "must_not_contain": [],
        "max_response_time": 20,
    },
    {
        "id": "TC005", "category": "多步推理",
        "input": "微软和苹果哪个更值得关注？",
        "must_contain": ["MSFT", "AAPL"],
        "must_not_contain": [],
        "max_response_time": 40,
    },
]

# ─────────────────────────────────────────
# 评测逻辑
# ─────────────────────────────────────────

def run_test(agent, tc):
    print(f"\n{'='*50}")
    print(f"[{tc['id']}] {tc['category']}")
    print(f"输入: {tc['input']}")
    print("-" * 50)

    result = {
        "id": tc["id"], "category": tc["category"],
        "input": tc["input"], "passed": False,
        "response": "", "response_time": 0, "failures": [],
    }

    try:
        start = time.time()
        output = agent.invoke({"messages": [HumanMessage(content=tc["input"])]})
        response = output["messages"][-1].content
        elapsed = round(time.time() - start, 2)

        result["response"] = response
        result["response_time"] = elapsed

        print(f"回答: {response[:200]}{'...' if len(response) > 200 else ''}")
        print(f"响应时间: {elapsed}s")

        for kw in tc["must_contain"]:
            if kw not in response:
                result["failures"].append(f"缺少关键词: '{kw}'")
        if elapsed > tc["max_response_time"]:
            result["failures"].append(f"响应超时: {elapsed}s")

        result["passed"] = len(result["failures"]) == 0

    except Exception as e:
        result["failures"].append(f"运行出错: {str(e)}")

    status = "✅ PASS" if result["passed"] else "❌ FAIL"
    print(f"结果: {status}")
    for f in result["failures"]:
        print(f"  → {f}")

    return result


def run_eval():
    print("=" * 50)
    print("  FinanceGPT Agent 自动化评测")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    agent = build_agent()
    results = []

    for tc in TEST_CASES:
        result = run_test(agent, tc)
        results.append(result)
        time.sleep(3)

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_time = round(sum(r["response_time"] for r in results) / total, 2)

    print(f"\n{'='*50}")
    print("  评测报告汇总")
    print("=" * 50)
    print(f"总用例:     {total}")
    print(f"通过:       {passed} ✅  失败: {total-passed} ❌")
    print(f"通过率:     {round(passed/total*100, 1)}%")
    print(f"平均响应:   {avg_time}s")

    print(f"\n{'分类':<12} {'ID':<8} {'结果':<8} {'耗时'}")
    print("-" * 40)
    for r in results:
        s = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"{r['category']:<12} {r['id']:<8} {s:<8} {r['response_time']}s")

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total, "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{round(passed/total*100, 1)}%",
            "avg_response_time": avg_time,
        },
        "results": results,
    }
    with open("eval_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📄 报告已保存到 eval_report.json")


if __name__ == "__main__":
    run_eval()
