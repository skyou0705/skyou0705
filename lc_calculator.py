import streamlit as st
import yfinance as yf
import datetime

# ==================== 基本設定 ====================
st.set_page_config(
    page_title="風險執行計算器",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 多語言支援 ====================
if 'language' not in st.session_state:
    st.session_state.language = "zh-tw"

trans = {
    "zh-tw": {
        "title": "⚔️ 風險執行計算器",
        "caption": "版本：雙雷達 (股價 + 實時外匯) 連動版",
        "funds_title": "💰 資金與標的",
        "exchange_label": "🔄 美金/馬幣 即時匯率",
        "system_fetch": " (系統抓取: {})",
        "watchlist_label": "📋 專屬軍火庫 (可打字搜尋)",
        "manual_input": "手動輸入",
        "ticker_label": "標的代號 (Ticker)",
        "usd_budget_label": "投入總預算 (USD)",
        "myr_budget_label": "投入總預算 (MYR)",
        "buy_price_label": "打算進場的價格 (USD)",
        "quantity_label": "最終確認購買股數",
        "percent_title": "🎯 戰術百分比 (%) 設定",
        "profit_slider": "📈 基準獲利目標 (%)",
        "stoploss_slider": "📉 基準停損底線 (%)",
        "take_profit_header": "獲利劇本 (Take Profit)",
        "stop_loss_header": "防禦劇本 (Stop Loss)",
        "scheme_a": "A 方案: 保守",
        "scheme_b": "B 方案: 達標",
        "scheme_c": "C 方案: 延伸",
        "stop_a": "A 方案: 撤退",
        "stop_b": "B 方案: 標準",
        "stop_c": "C 方案: 極限",
        "target_price": "目標價",
        "trigger_price": "觸發價",
        "net_profit": "淨賺",
        "net_loss": "淨虧",
        "budget_warning": "⚠️ 預算不足以購買 1 股並支付手續費。",
        "quote_time": "⏱️ 報價時間: {}",
        # 新增：實行數據
        "execution_title": "實行數據：",
        "input_label": "投入：",
        "purchase_label": "購買 ：",
        "remaining_label": "剩餘資金:",
    },
    "zh-cn": {
        "title": "⚔️ 风险执行计算器",
        "caption": "版本：双雷达 (股价 + 实时外汇) 联动版",
        "funds_title": "💰 资金与标的",
        "exchange_label": "🔄 美元/马币 实时汇率",
        "system_fetch": " (系统抓取: {})",
        "watchlist_label": "📋 专属军火库 (可打字搜索)",
        "manual_input": "手动输入",
        "ticker_label": "标的代码 (Ticker)",
        "usd_budget_label": "投入总预算 (USD)",
        "myr_budget_label": "投入总预算 (MYR)",
        "buy_price_label": "打算进场的价格 (USD)",
        "quantity_label": "最终确认购买股数",
        "percent_title": "🎯 战术百分比 (%) 设定",
        "profit_slider": "📈 基准获利目标 (%)",
        "stoploss_slider": "📉 基准止损底线 (%)",
        "take_profit_header": "获利剧本 (Take Profit)",
        "stop_loss_header": "防御剧本 (Stop Loss)",
        "scheme_a": "A 方案: 保守",
        "scheme_b": "B 方案: 达标",
        "scheme_c": "C 方案: 延伸",
        "stop_a": "A 方案: 撤退",
        "stop_b": "B 方案: 标准",
        "stop_c": "C 方案: 极限",
        "target_price": "目标价",
        "trigger_price": "触发价",
        "net_profit": "净赚",
        "net_loss": "净亏",
        "budget_warning": "⚠️ 预算不足以购买 1 股并支付手续费。",
        "quote_time": "⏱️ 报价时间: {}",
        "execution_title": "实行数据：",
        "input_label": "投入：",
        "purchase_label": "购买 ：",
        "remaining_label": "剩余资金:",
    },
    "en": {
        "title": "⚔️ Risk Execution Calculator",
        "caption": "Version: Dual Radar (Stock + Real-time FX) Linked",
        "funds_title": "💰 Funds & Target",
        "exchange_label": "🔄 USD/MYR Live Rate",
        "system_fetch": " (System: {})",
        "watchlist_label": "📋 Watchlist (Searchable)",
        "manual_input": "Manual Input",
        "ticker_label": "Ticker Symbol",
        "usd_budget_label": "Total Budget (USD)",
        "myr_budget_label": "Total Budget (MYR)",
        "buy_price_label": "Planned Entry Price (USD)",
        "quantity_label": "Final Confirmed Shares",
        "percent_title": "🎯 Tactical Percentage (%) Settings",
        "profit_slider": "📈 Target Profit (%)",
        "stoploss_slider": "📉 Base Stop Loss (%)",
        "take_profit_header": "Take Profit Plans",
        "stop_loss_header": "Stop Loss Plans",
        "scheme_a": "A: Conservative",
        "scheme_b": "B: Target",
        "scheme_c": "C: Extended",
        "stop_a": "A: Retreat",
        "stop_b": "B: Standard",
        "stop_c": "C: Extreme",
        "target_price": "Target Price",
        "trigger_price": "Trigger Price",
        "net_profit": "Net Profit",
        "net_loss": "Net Loss",
        "budget_warning": "⚠️ Budget not enough for 1 share + commission.",
        "quote_time": "⏱️ Quote Time: {}",
        "execution_title": "Execution Data:",
        "input_label": "Invested:",
        "purchase_label": "Purchased:",
        "remaining_label": "Remaining Funds:",
    }
}

lang = st.session_state.language

# ==================== 高級外觀 CSS（標題已縮小） ====================
st.markdown("""
<style>
    .big-title {
        font-size: 2.45rem !important;   /* 已調小，更專業舒服 */
        font-weight: 700;
        background: linear-gradient(90deg, #FFD700, #FFAA00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .stApp { background-color: #0E1117; }
    .stButton>button { font-size: 1.1rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==================== 右上角語言按鈕 ====================
header_cols = st.columns([6, 1, 1, 1, 1])
with header_cols[0]:
    st.markdown(f'<h1 class="big-title">{trans[lang]["title"]}</h1>', unsafe_allow_html=True)

with header_cols[2]:
    if st.button("繁", key="btn_zhtw", use_container_width=True):
        st.session_state.language = "zh-tw"
        st.rerun()
with header_cols[3]:
    if st.button("简", key="btn_zhcn", use_container_width=True):
        st.session_state.language = "zh-cn"
        st.rerun()
with header_cols[4]:
    if st.button("EN", key="btn_en", use_container_width=True):
        st.session_state.language = "en"
        st.rerun()

st.caption(trans[lang]["caption"])

# ==================== 其他功能（匯率、軍火庫、slider、刻度尺、報表）全部保留不變 ====================
# （為了篇幅這裡省略中間完全相同的程式碼，請直接把你上一個版本的「匯率功能、資金與標的、百分比設定、刻度尺、作戰報表」全部貼上來，只替換下面這一段「實行數據」即可）

# ==================== 實行數據（已改成你指定的格式） ====================
if quantity > 0:
    rm_value = real_capital * st.session_state.exchange_rate
    remaining = total_budget - real_capital
    st.markdown(f"""
    ### {trans[lang]["execution_title"]}
    **{trans[lang]["input_label"]}** ${real_capital:.2f} USD (約 RM {rm_value:.2f})  
    **{trans[lang]["purchase_label"]}** {quantity} 股 {ticker}。  
    **{trans[lang]["remaining_label"]}** ${remaining:.2f} USD
    """, unsafe_allow_html=True)
elif total_budget > 0:
    st.warning(trans[lang]["budget_warning"])

st.divider()

# ==================== 後面獲利/停損報表（完全不變） ====================
if quantity > 0:
    # ...（把你之前版本的獲利劇本 + 防禦劇本程式碼直接貼在這裡）
    pass  # ← 這裡請貼上你原本的 p_col1 / p_col2 / p_col3 和 s_col1 / s_col2 / s_col3 部分
