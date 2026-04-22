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
        "max_quantity_hint": "最多可買",
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
        "execution_title": "實行數據：",
        "disclaimer": "**免責聲明**：本工具僅供參考，不構成任何投資建議。過去表現不代表未來結果。本計算機僅為輔助工具，所有數據及計算結果僅供參考，請自行判斷風險並承擔一切後果。"
    },
    "zh-cn": { ... },  # 簡中內容與之前相同（disclaimer 已正確）
    "en": { ... }      # 英文內容與之前相同
}

lang = st.session_state.language

# ==================== CSS（實行數據字體已再調小） ====================
st.markdown("""
<style>
    .big-title {
        font-size: 2.45rem !important;
        font-weight: 700;
        background: linear-gradient(90deg, #FFD700, #FFAA00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .execution-data { 
        font-size: 0.98rem !important;   /* 已再調小 */
        line-height: 1.75; 
    }
    .stApp { background-color: #0E1117; }
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

# ==================== 匯率、平台、資金區塊（不變） ====================
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

st.subheader(trans[lang]["funds_title"])
st.number_input(trans[lang]["exchange_label"] + trans[lang]["system_fetch"].format(live_rate),
                min_value=3.0, max_value=6.0, step=0.01, key="exchange_rate", on_change=update_rate)

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
    ticker = st.text_input(trans[lang]["ticker_label"], key="target_ticker").upper()
with col2:
    st.number_input(trans[lang]["usd_budget_label"], min_value=0.0, step=10.0, key="usd_budget", on_change=update_myr)
with col3:
    st.number_input(trans[lang]["myr_budget_label"], min_value=0.0, step=50.0, key="myr_budget", on_change=update_usd)

total_budget = st.session_state.usd_budget

# 股價與股數（不變）
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
    buy_price = st.number_input(trans[lang]["buy_price_label"], min_value=0.01,
                                value=float(current_price) if current_price > 0 else 13.29, step=0.01)
    if fetch_time_str:
        st.caption(trans[lang]["quote_time"].format(fetch_time_str))

max_quantity = int(max(0, (total_budget - platform_fee) // buy_price)) if buy_price > 0 else 0
st.caption(f"**{trans[lang]['max_quantity_hint']}：{max_quantity} 股**")

with col5:
    quantity = st.number_input(trans[lang]["quantity_label"], min_value=0, value=max_quantity, step=1)

# ==================== 實行數據（已完全按照你要求調整） ====================
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

# ==================== 百分比設定 + ABC 劇本（不變） ====================
# （這裡貼上你上一個版本的百分比 slider、刻度尺、獲利劇本 ABC、停損劇本 ABC 完整程式碼）
# ...（為節省篇幅不再重複，你直接把上一個版本從「戰術百分比設定」到結尾全部貼上即可）

st.markdown("---")
st.caption(trans[lang]["disclaimer"])
