import streamlit as st
import yfinance as yf
import datetime

# ==================== 基本設定 ====================
st.set_page_config(
    page_title="戰術狙擊計算機",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 多語言支援 ====================
if 'language' not in st.session_state:
    st.session_state.language = "zh-tw"

trans = {
    "zh-tw": {
        "title": "⚔️ 戰術狙擊計算機",
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
        "real_data": "**實戰數據：** 投入 **${:.2f} USD** (約 RM {:.2f}) 購買 **{}** 股 {}。\n\n剩餘資金: ${:.2f} USD",
        "budget_warning": "⚠️ 預算不足以購買 1 股並支付手續費。",
        "quote_time": "⏱️ 報價時間: {}",
    },
    "zh-cn": {  # 簡中內容與上次一致，這裡省略重複，實際使用時請保留完整字典
        "title": "⚔️ 战术狙击计算器",
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
        "real_data": "**实战数据：** 投入 **${:.2f} USD** (约 RM {:.2f}) 购买 **{}** 股 {}。\n\n剩余资金: ${:.2f} USD",
        "budget_warning": "⚠️ 预算不足以购买 1 股并支付手续费。",
        "quote_time": "⏱️ 报价时间: {}",
    },
    "en": {  # 英文內容與上次一致
        "title": "⚔️ Tactical Sniper Calculator",
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
        "real_data": "**Battle Data:** Invested **${:.2f} USD** (≈ RM {:.2f}) to buy **{}** shares of {}.\n\nRemaining: ${:.2f} USD",
        "budget_warning": "⚠️ Budget not enough for 1 share + commission.",
        "quote_time": "⏱️ Quote Time: {}",
    }
}

lang = st.session_state.language

# ==================== 高級外觀 CSS ====================
st.markdown("""
<style>
    .big-title {
        font-size: 2.8rem !important;
        font-weight: 700;
        background: linear-gradient(90deg, #FFD700, #FFAA00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
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

# ==================== 匯率與預算功能（不變） ====================
@st.cache_data(ttl=3600)
def get_live_exchange_rate():
    try:
        rate = yf.Ticker("USDMYR=X").fast_info.last_price
        return round(rate, 4)
    except Exception:
        return 3.955

live_rate = get_live_exchange_rate()

for k, v in [("usd_budget", 0.0), ("exchange_rate", live_rate), ("myr_budget", 0.0), ("target_ticker", "TSLL")]:
    if k not in st.session_state:
        st.session_state[k] = v

def update_myr(): st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate
def update_usd(): st.session_state.usd_budget = st.session_state.myr_budget / st.session_state.exchange_rate
def update_rate(): st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate
def sync_quick_pick():
    if st.session_state.quick_pick != trans["zh-tw"]["manual_input"]:
        st.session_state.target_ticker = st.session_state.quick_pick

# 資金與標的
st.subheader(trans[lang]["funds_title"])
st.number_input(
    trans[lang]["exchange_label"] + trans[lang]["system_fetch"].format(live_rate),
    min_value=3.0, max_value=6.0, step=0.01,
    key="exchange_rate", on_change=update_rate
)

watchlist_base = ["TSLL", "MSFU", "METU", "INTC", "PEP", "SOFI", "CPB", "CAG", "GIS", "NVDL", "AMDL", "AAPU", "LUMN", "ROOT", "HIMS", "KGC"]
watchlist = [trans[lang]["manual_input"]] + watchlist_base
st.selectbox(trans[lang]["watchlist_label"], watchlist, key="quick_pick", on_change=sync_quick_pick)

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input(trans[lang]["ticker_label"], key="target_ticker").upper()
with col2:
    st.number_input(trans[lang]["usd_budget_label"], min_value=0.0, step=10.0, key="usd_budget", on_change=update_myr)
with col3:
    st.number_input(trans[lang]["myr_budget_label"], min_value=0.0, step=50.0, key="myr_budget", on_change=update_usd)

total_budget = st.session_state.usd_budget

current_price = 0.00
fetch_time_str = ""
if ticker:
    try:
        stock_info = yf.Ticker(ticker)
        current_price = stock_info.fast_info.last_price
        fetch_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        current_price = 0.00

col4, col5 = st.columns(2)
with col4:
    buy_price = st.number_input(
        trans[lang]["buy_price_label"],
        min_value=0.01,
        value=float(current_price) if current_price > 0 else 13.29,
        step=0.01
    )
    if fetch_time_str:
        st.caption(trans[lang]["quote_time"].format(fetch_time_str))

buy_fee = sell_fee = 1.0
max_quantity = int(max(0, (total_budget - buy_fee) // buy_price)) if buy_price > 0 else 0
with col5:
    quantity = st.number_input(trans[lang]["quantity_label"], min_value=0, value=max_quantity, step=1)

real_capital = (buy_price * quantity) + buy_fee

if quantity > 0:
    st.info(trans[lang]["real_data"].format(
        real_capital, real_capital * st.session_state.exchange_rate,
        quantity, ticker, total_budget - real_capital
    ))
elif total_budget > 0:
    st.warning(trans[lang]["budget_warning"])

st.divider()

# ==================== 戰術百分比設定（重點：已加上刻度尺） ====================
st.subheader(trans[lang]["percent_title"])
t_col1, t_col2 = st.columns(2)

with t_col1:
    target_profit_pct = st.slider(
        trans[lang]["profit_slider"], 
        min_value=1.0, 
        max_value=100.0, 
        value=3.0, 
        step=0.5
    )
    # 獲利目標刻度尺（下方尺標）
    st.markdown('''
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#999; margin:-8px 0 12px 0; padding:0 8px;">
            <div>1%</div><div>20%</div><div>40%</div><div>60%</div><div>80%</div><div>100%</div>
        </div>
    ''', unsafe_allow_html=True)

with t_col2:
    base_stop_loss_pct = st.slider(
        trans[lang]["stoploss_slider"], 
        min_value=0.5, 
        max_value=10.0, 
        value=2.0, 
        step=0.5
    )
    # 停損刻度尺（下方尺標）
    st.markdown('''
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#999; margin:-8px 0 12px 0; padding:0 8px;">
            <div>0.5%</div><div>2%</div><div>4%</div><div>6%</div><div>8%</div><div>10%</div>
        </div>
    ''', unsafe_allow_html=True)

st.divider()

# ==================== 作戰報表（不變） ====================
if quantity > 0:
    st.markdown(f"### 📈 {ticker} {trans[lang]['take_profit_header']}")
    p_col1, p_col2, p_col3 = st.columns(3)
    
    pct_a = max(1.0, target_profit_pct - 3.0)
    price_a = buy_price * (1 + pct_a / 100)
    profit_a = (price_a * quantity) - real_capital - sell_fee
    p_col1.success(f"**{trans[lang]['scheme_a']} (+{pct_a:.1f}%)**\n\n{trans[lang]['target_price']}: **${price_a:.2f}**\n\n{trans[lang]['net_profit']}: **${profit_a:.2f}**\n\n(約 RM {profit_a * st.session_state.exchange_rate:.0f})")

    pct_b = target_profit_pct
    price_b = buy_price * (1 + pct_b / 100)
    profit_b = (price_b * quantity) - real_capital - sell_fee
    p_col2.warning(f"**{trans[lang]['scheme_b']} (+{pct_b:.1f}%)**\n\n{trans[lang]['target_price']}: **${price_b:.2f}**\n\n{trans[lang]['net_profit']}: **${profit_b:.2f}**\n\n(約 RM {profit_b * st.session_state.exchange_rate:.0f})")

    pct_c = target_profit_pct + 3.0
    price_c = buy_price * (1 + pct_c / 100)
    profit_c = (price_c * quantity) - real_capital - sell_fee
    p_col3.success(f"**{trans[lang]['scheme_c']} (+{pct_c:.1f}%)**\n\n{trans[lang]['target_price']}: **${price_c:.2f}**\n\n{trans[lang]['net_profit']}: **${profit_c:.2f}**\n\n(約 RM {profit_c * st.session_state.exchange_rate:.0f})")

    st.markdown(f"### 📉 {ticker} {trans[lang]['stop_loss_header']}")
    s_col1, s_col2, s_col3 = st.columns(3)
    
    sl_a = max(0.5, base_stop_loss_pct - 0.5)
    sl_price_a = buy_price * (1 - sl_a / 100)
    sl_loss_a = (sl_price_a * quantity) - real_capital - sell_fee
    s_col1.error(f"**{trans[lang]['stop_a']} (-{sl_a:.1f}%)**\n\n{trans[lang]['trigger_price']}: **${sl_price_a:.2f}**\n\n{trans[lang]['net_loss']}: **${sl_loss_a:.2f}**\n\n(約 RM {sl_loss_a * st.session_state.exchange_rate:.0f})")

    sl_price_b = buy_price * (1 - base_stop_loss_pct / 100)
    sl_loss_b = (sl_price_b * quantity) - real_capital - sell_fee
    s_col2.error(f"**{trans[lang]['stop_b']} (-{base_stop_loss_pct:.1f}%)**\n\n{trans[lang]['trigger_price']}: **${sl_price_b:.2f}**\n\n{trans[lang]['net_loss']}: **${sl_loss_b:.2f}**\n\n(約 RM {sl_loss_b * st.session_state.exchange_rate:.0f})")

    sl_c = base_stop_loss_pct + 0.5
    sl_price_c = buy_price * (1 - sl_c / 100)
    sl_loss_c = (sl_price_c * quantity) - real_capital - sell_fee
    s_col3.error(f"**{trans[lang]['stop_c']} (-{sl_c:.1f}%)**\n\n{trans[lang]['trigger_price']}: **${sl_price_c:.2f}**\n\n{trans[lang]['net_loss']}: **${sl_loss_c:.2f}**\n\n(約 RM {sl_loss_c * st.session_state.exchange_rate:.0f})")
