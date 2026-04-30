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

# ==================== 多語言 ====================
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
        "platform_label": "交易平台",
        "moomoo_option": "Moomoo (MY)",
        "usd_budget_label": "投入總預算 (USD)",
        "myr_budget_label": "投入總預算 (MYR)",
        "buy_price_label": "打算進場的價格 (USD)",
        "quantity_label": "最終確認購買股數",
        "percent_title": "🎯 戰術百分比 (%) 設定",
        "profit_slider": "📈 基準獲利目標 (%)",
        "stoploss_slider": "📉 基準停損底線 (%)",
        "cents_toggle": "仙位顯示",
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
        "execution_title": "實行數據：",
        "disclaimer": "**免責聲明**：本工具僅供參考，不構成任何投資建議。過去表現不代表未來結果。本計算機僅為輔助工具，所有數據及計算結果僅供參考，請自行判斷風險並承擔一切後果。"
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
        "platform_label": "交易平台",
        "moomoo_option": "Moomoo (MY)",
        "usd_budget_label": "投入总预算 (USD)",
        "myr_budget_label": "投入总预算 (MYR)",
        "buy_price_label": "打算进场的价格 (USD)",
        "quantity_label": "最终确认购买股数",
        "percent_title": "🎯 战术百分比 (%) 设定",
        "profit_slider": "📈 基准获利目标 (%)",
        "stoploss_slider": "📉 基准止损底线 (%)",
        "cents_toggle": "仙位显示",
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
        "disclaimer": "**免责声明**：本工具仅供参考，不构成任何投资建议。过去表现不代表未来结果。本计算机仅为辅助工具，所有数据及计算结果仅供参考，请自行判断风险并承担一切后果。"
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
        "platform_label": "Trading Platform",
        "moomoo_option": "Moomoo (MY)",
        "usd_budget_label": "Total Budget (USD)",
        "myr_budget_label": "Total Budget (MYR)",
        "buy_price_label": "Planned Entry Price (USD)",
        "quantity_label": "Final Confirmed Shares",
        "percent_title": "🎯 Tactical Percentage (%) Settings",
        "profit_slider": "📈 Target Profit (%)",
        "stoploss_slider": "📉 Base Stop Loss (%)",
        "cents_toggle": "Show Cents",
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
        "disclaimer": "**Disclaimer**: This tool is for reference only and does not constitute investment advice. Past performance does not indicate future results. All calculations are for reference only. Please assess risks yourself and bear all consequences."
    }
}

lang = st.session_state.language

# ==================== CSS ====================
st.markdown("""
<style>
    .big-title { font-size: 2.45rem !important; font-weight: 700; background: linear-gradient(90deg, #FFD700, #FFAA00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.3rem; letter-spacing: -0.5px; }
    .execution-data { font-size: 0.98rem !important; line-height: 1.75; }
    .stApp { background-color: #0E1117; }
</style>
""", unsafe_allow_html=True)

# ==================== 右上角語言按鈕 ====================
header_cols = st.columns([6, 1, 1, 1, 1])
with header_cols[0]:
    st.markdown(f'<h1 class="big-title">{trans[lang]["title"]}</h1>', unsafe_allow_html=True)
with header_cols[2]:
    if st.button("繁", key="btn_zhtw", use_container_width=True):
        st.session_state.language = "zh-tw"; st.rerun()
with header_cols[3]:
    if st.button("简", key="btn_zhcn", use_container_width=True):
        st.session_state.language = "zh-cn"; st.rerun()
with header_cols[4]:
    if st.button("EN", key="btn_en", use_container_width=True):
        st.session_state.language = "en"; st.rerun()

st.caption(trans[lang]["caption"])

# ==================== 匯率、平台、資金 ====================
@st.cache_data(ttl=3600)
def get_live_exchange_rate():
    try:
        rate = yf.Ticker("USDMYR=X").fast_info.last_price
        return round(rate, 4)
    except Exception:
        return 3.955

live_rate = get_live_exchange_rate()

for k, v in [("usd_budget", 0.0), ("exchange_rate", live_rate), ("myr_budget", 0.0), ("target_ticker", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

def update_myr(): st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate
def update_usd(): st.session_state.usd_budget = st.session_state.myr_budget / st.session_state.exchange_rate
def update_rate(): st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate
def sync_quick_pick():
    if st.session_state.quick_pick != trans["zh-tw"]["manual_input"]:
        st.session_state.target_ticker = st.session_state.quick_pick

st.subheader(trans[lang]["funds_title"])
st.number_input(trans[lang]["exchange_label"] + trans[lang]["system_fetch"].format(live_rate), min_value=3.0, max_value=6.0, step=0.01, key="exchange_rate", on_change=update_rate)

watchlist_base = ["TSLL", "MSFU", "METU", "INTC", "PEP", "SOFI", "CPB", "CAG", "GIS", "NVDL", "AMDL", "AAPU", "LUMN", "ROOT", "HIMS", "KGC"]
watchlist = [trans[lang]["manual_input"]] + watchlist_base
st.selectbox(trans[lang]["watchlist_label"], watchlist, key="quick_pick", on_change=sync_quick_pick)

col_platform, _ = st.columns(2)
with col_platform:
    platform_options = [trans[lang]["moomoo_option"], trans[lang]["manual_input"]]
    platform = st.selectbox(trans[lang]["platform_label"], platform_options, key="platform")

is_moomoo = platform == trans[lang]["moomoo_option"]
commission_rate = 0.0003 if is_moomoo else 0.0
platform_fee = 0.99 if is_moomoo else 1.0

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input(trans[lang]["ticker_label"], key="target_ticker", value="").upper()
with col2:
    st.number_input(trans[lang]["usd_budget_label"], min_value=0.0, step=10.0, key="usd_budget", on_change=update_myr)
with col3:
    st.number_input(trans[lang]["myr_budget_label"], min_value=0.0, step=50.0, key="myr_budget", on_change=update_usd)

total_budget = st.session_state.usd_budget

# ==================== 股價抓取 ====================
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
        min_value=0.0,           # ← 改成 0.0
        value=0.0,               # ← 預設改成 0
        step=0.0001,             # ← 支援仙位
        format="%.4f"
    )
    if fetch_time_str:
        st.caption(trans[lang]["quote_time"].format(fetch_time_str))

# ==================== 股數 ====================
max_quantity = int(max(0, (total_budget - platform_fee) // buy_price)) if buy_price > 0 else 0

with col5:
    quantity = st.number_input(trans[lang]["quantity_label"], min_value=0, value=max_quantity, step=1)

# ==================== 實行數據 ====================
real_capital = buy_price * quantity + platform_fee + (commission_rate * buy_price * quantity if commission_rate > 0 else 0)
remaining = total_budget - real_capital

if quantity > 0:
    rm_value = real_capital * st.session_state.exchange_rate
    st.markdown(f"""
    ### {trans[lang]["execution_title"]}
    <div class="execution-data">
    💰 投入： ${real_capital:.2f} USD (約 RM {rm_value:.2f})<br>
    📈 購買 ： {quantity} 股 {ticker}。<br>
    💵 剩餘資金: ${remaining:.2f} USD
    </div>
    """, unsafe_allow_html=True)
elif total_budget > 0:
    st.warning(trans[lang]["budget_warning"])

st.divider()

# ==================== 戰術百分比設定 ====================
st.subheader(trans[lang]["percent_title"])
t_col1, t_col2 = st.columns(2)

with t_col1:
    target_profit_pct = st.slider(trans[lang]["profit_slider"], 1.0, 200.0, 3.0, step=1.0)
    st.markdown('''
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#999; margin:-8px 0 12px 0; padding:0 8px;">
            <div>1%</div><div>20%</div><div>40%</div><div>60%</div><div>80%</div><div>100%</div><div>120%</div><div>140%</div><div>160%</div><div>180%</div><div>200%</div>
        </div>
    ''', unsafe_allow_html=True)

with t_col2:
    base_stop_loss_pct = st.slider(trans[lang]["stoploss_slider"], 0.5, 10.0, 2.0, step=0.5)
    st.markdown('''
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#999; margin:-8px 0 12px 0; padding:0 8px;">
            <div>0.5%</div><div>2%</div><div>4%</div><div>6%</div><div>8%</div><div>10%</div>
        </div>
    ''', unsafe_allow_html=True)

cents_mode = st.toggle(trans[lang]["cents_toggle"], value=False, key="cents_mode")

st.divider()

# ==================== 價格格式化 ====================
def format_price(price, cents_mode):
    return f"${price:.4f}" if cents_mode else f"${price:.2f}"

# ==================== 獲利 / 停損劇本 ====================
if quantity > 0:
    st.markdown(f"### 📈 {ticker} {trans[lang]['take_profit_header']}")
    p_col1, p_col2, p_col3 = st.columns(3)
    
    pct_a = max(1.0, target_profit_pct - 3.0)
    price_a = max(0.01, buy_price * (1 + pct_a / 100))
    profit_a = (price_a * quantity) - real_capital - (platform_fee + commission_rate * price_a * quantity if commission_rate > 0 else 0)
    p_col1.success(f"**{trans[lang]['scheme_a']} (+{pct_a:.1f}%)**\n\n{trans[lang]['target_price']}: **{format_price(price_a, cents_mode)}**\n\n{trans[lang]['net_profit']}: **${profit_a:.2f}**\n\n(約 RM {profit_a * st.session_state.exchange_rate:.0f})")

    pct_b = target_profit_pct
    price_b = max(0.01, buy_price * (1 + pct_b / 100))
    profit_b = (price_b * quantity) - real_capital - (platform_fee + commission_rate * price_b * quantity if commission_rate > 0 else 0)
    p_col2.warning(f"**{trans[lang]['scheme_b']} (+{pct_b:.1f}%)**\n\n{trans[lang]['target_price']}: **{format_price(price_b, cents_mode)}**\n\n{trans[lang]['net_profit']}: **${profit_b:.2f}**\n\n(約 RM {profit_b * st.session_state.exchange_rate:.0f})")

    pct_c = target_profit_pct + 3.0
    price_c = max(0.01, buy_price * (1 + pct_c / 100))
    profit_c = (price_c * quantity) - real_capital - (platform_fee + commission_rate * price_c * quantity if commission_rate > 0 else 0)
    p_col3.success(f"**{trans[lang]['scheme_c']} (+{pct_c:.1f}%)**\n\n{trans[lang]['target_price']}: **{format_price(price_c, cents_mode)}**\n\n{trans[lang]['net_profit']}: **${profit_c:.2f}**\n\n(約 RM {profit_c * st.session_state.exchange_rate:.0f})")

    st.markdown(f"### 📉 {ticker} {trans[lang]['stop_loss_header']}")
    s_col1, s_col2, s_col3 = st.columns(3)
    
    sl_a = max(0.5, base_stop_loss_pct - 0.5)
    sl_price_a = max(0.01, buy_price * (1 - sl_a / 100))
    sl_loss_a = (sl_price_a * quantity) - real_capital - (platform_fee + commission_rate * sl_price_a * quantity if commission_rate > 0 else 0)
    s_col1.error(f"**{trans[lang]['stop_a']} (-{sl_a:.1f}%)**\n\n{trans[lang]['trigger_price']}: **{format_price(sl_price_a, cents_mode)}**\n\n{trans[lang]['net_loss']}: **${sl_loss_a:.2f}**\n\n(約 RM {sl_loss_a * st.session_state.exchange_rate:.0f})")

    sl_price_b = max(0.01, buy_price * (1 - base_stop_loss_pct / 100))
    sl_loss_b = (sl_price_b * quantity) - real_capital - (platform_fee + commission_rate * sl_price_b * quantity if commission_rate > 0 else 0)
    s_col2.error(f"**{trans[lang]['stop_b']} (-{base_stop_loss_pct:.1f}%)**\n\n{trans[lang]['trigger_price']}: **{format_price(sl_price_b, cents_mode)}**\n\n{trans[lang]['net_loss']}: **${sl_loss_b:.2f}**\n\n(約 RM {sl_loss_b * st.session_state.exchange_rate:.0f})")

    sl_c = base_stop_loss_pct + 0.5
    sl_price_c = max(0.01, buy_price * (1 - sl_c / 100))
    sl_loss_c = (sl_price_c * quantity) - real_capital - (platform_fee + commission_rate * sl_price_c * quantity if commission_rate > 0 else 0)
    s_col3.error(f"**{trans[lang]['stop_c']} (-{sl_c:.1f}%)**\n\n{trans[lang]['trigger_price']}: **{format_price(sl_price_c, cents_mode)}**\n\n{trans[lang]['net_loss']}: **${sl_loss_c:.2f}**\n\n(約 RM {sl_loss_c * st.session_state.exchange_rate:.0f})")

    st.markdown("---")
    st.caption(trans[lang]["disclaimer"])
