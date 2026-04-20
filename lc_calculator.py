import streamlit as st
import yfinance as yf
import datetime

# 設定網頁標題與版面
st.set_page_config(page_title="戰術計算機", page_icon="⚔️", layout="centered")

# --- 🌟 新增：外匯雷達 (自動抓取即時匯率) ---
@st.cache_data(ttl=3600)  # 快取 1 小時，避免頻繁讀取拖慢速度
def get_live_exchange_rate():
    try:
        # USDMYR=X 是美金對馬幣的外匯代號
        rate = yf.Ticker("USDMYR=X").fast_info.last_price
        return round(rate, 4) # 取小數點後四位
    except Exception:
        return 4 # 如果網路斷線，使用備用預設值

# 啟動時獲取真實匯率
live_rate = get_live_exchange_rate()

# --- 匯率與預算雙向連動邏輯 (Session State) ---
if 'usd_budget' not in st.session_state:
    st.session_state.usd_budget = 0.0
if 'exchange_rate' not in st.session_state:
    st.session_state.exchange_rate = live_rate  # 改為使用剛剛抓到的真實匯率！
if 'myr_budget' not in st.session_state:
    st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate
if 'target_ticker' not in st.session_state:
    st.session_state.target_ticker = "TSLL"

def update_myr():
    st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate

def update_usd():
    st.session_state.usd_budget = st.session_state.myr_budget / st.session_state.exchange_rate

def update_rate():
    st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate

def sync_quick_pick():
    if st.session_state.quick_pick != "手動輸入":
        st.session_state.target_ticker = st.session_state.quick_pick

st.title("⚔️ 戰術狙擊計算機")
st.caption("版本：雙雷達 (股價 + 實時外匯) 連動版")

# --- 第一區：資金與標的 ---
st.subheader("💰 資金與標的")

# 匯率輸入框，預設值已變成真實匯率
st.number_input(f"🔄 美金/馬幣 即時匯率 (系統抓取: {live_rate})", min_value=3.0, max_value=6.0, step=0.01, 
                key="exchange_rate", on_change=update_rate, help="已自動抓取國際外匯即時價格，可根據銀行實際換匯成本微調")

# 軍火庫快速選單
watchlist = ["手動輸入", "TSLL", "MSFU", "METU", "INTC", "PEP", "SOFI", "CPB", "CAG", "GIS", "NVDA", "TSLA", "AAPL", "LUMN"]
st.selectbox("📋 專屬軍火庫 (可打字搜尋)", watchlist, key="quick_pick", on_change=sync_quick_pick)

col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("標的代號 (Ticker)", key="target_ticker").upper()

with col2:
    st.number_input("投入總預算 (USD)", min_value=0.0, step=10.0, 
                    key="usd_budget", on_change=update_myr)

with col3:
    st.number_input("投入總預算 (MYR)", min_value=0.0, step=50.0, 
                    key="myr_budget", on_change=update_usd)

total_budget = st.session_state.usd_budget

# 啟動自動抓價雷達與時間
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
    buy_price = st.number_input("打算進場的價格 (USD)", min_value=0.01, 
                                value=float(current_price) if current_price > 0 else 11.42, 
                                step=0.01)
    st.write("") 
    if fetch_time_str:
        st.caption(f"⏱️ 報價時間: {fetch_time_str}")

buy_fee = 1.0
sell_fee = 1.0

# 確保計算出來的股數絕對不會是負數
if buy_price > 0:
    raw_qty = (total_budget - buy_fee) // buy_price
    max_quantity = int(max(0, raw_qty))
else:
    max_quantity = 0

with col5:
    quantity = st.number_input("最終確認購買股數", min_value=0, value=max_quantity, step=1)
    
real_capital = (buy_price * quantity) + buy_fee

if quantity > 0:
    st.info(f"**實戰數據：** 投入 **${real_capital:.2f} USD** (約 RM {real_capital * st.session_state.exchange_rate:.2f}) 購買 **{quantity}** 股 {ticker}。 \n\n 剩餘閒置資金: ${total_budget - real_capital:.2f} USD")
elif total_budget > 0:
    st.warning("⚠️ 預算不足以購買 1 股並支付手續費。")

st.divider()

# --- 第二區：雙拉桿設定 ---
st.subheader("🎯 戰術百分比 (%) 設定")

t_col1, t_col2 = st.columns(2)
with t_col1:
    target_profit_pct = st.slider("📈 基準獲利目標 (%)", min_value=1.0, max_value=30.0, value=8.0, step=0.5)
with t_col2:
    base_stop_loss_pct = st.slider("📉 基準停損底線 (%)", min_value=1.0, max_value=10.0, value=2.5, step=0.5)

st.divider()

# --- 第三區：作戰報表 ---
if quantity > 0:
    # ================= 獲利 ABC 劇本 =================
    st.markdown(f"### 📈 {ticker} 獲利劇本 (Take Profit)")
    p_col1, p_col2, p_col3 = st.columns(3)

    pct_a = max(1.0, target_profit_pct - 3.0)
    price_a = buy_price * (1 + (pct_a / 100))
    profit_a = (price_a * quantity) - real_capital - sell_fee
    p_col1.success(f"**A 方案: 保守 (+{pct_a:.1f}%)**\n\n目標價: **${price_a:.2f}**\n\n淨賺: **${profit_a:.2f}**\n\n**(約 RM {profit_a * st.session_state.exchange_rate:.0f})**")

    pct_b = target_profit_pct
    price_b = buy_price * (1 + (pct_b / 100))
    profit_b = (price_b * quantity) - real_capital - sell_fee
    p_col2.warning(f"**B 方案: 達標 (+{pct_b:.1f}%)**\n\n目標價: **${price_b:.2f}**\n\n淨賺: **${profit_b:.2f}**\n\n**(約 RM {profit_b * st.session_state.exchange_rate:.0f})**")

    pct_c = target_profit_pct + 3.0
    price_c = buy_price * (1 + (pct_c / 100))
    profit_c = (price_c * quantity) - real_capital - sell_fee
    p_col3.success(f"**C 方案: 延伸 (+{pct_c:.1f}%)**\n\n目標價: **${price_c:.2f}**\n\n淨賺: **${profit_c:.2f}**\n\n**(約 RM {profit_c * st.session_state.exchange_rate:.0f})**")

    # ================= 停損 ABC 劇本 =================
    st.markdown(f"### 📉 {ticker} 防禦劇本 (Stop Loss)")
    s_col1, s_col2, s_col3 = st.columns(3)

    sl_b = base_stop_loss_pct
    sl_a = max(0.5, sl_b - 0.5)
    sl_c = sl_b + 0.5

    sl_price_a = buy_price * (1 - (sl_a / 100))
    sl_loss_a = (sl_price_a * quantity) - real_capital - sell_fee
    s_col1.error(f"**A 方案: 撤退 (-{sl_a:.1f}%)**\n\n觸發價: **${sl_price_a:.2f}**\n\n淨虧: **${sl_loss_a:.2f}**\n\n**(約 RM {sl_loss_a * st.session_state.exchange_rate:.0f})**")

    sl_price_b = buy_price * (1 - (sl_b / 100))
    sl_loss_b = (sl_price_b * quantity) - real_capital - sell_fee
    s_col2.error(f"**B 方案: 標準 (-{sl_b:.1f}%)**\n\n觸發價: **${sl_price_b:.2f}**\n\n淨虧: **${sl_loss_b:.2f}**\n\n**(約 RM {sl_loss_b * st.session_state.exchange_rate:.0f})**")

    sl_price_c = buy_price * (1 - (sl_c / 100))
    sl_loss_c = (sl_price_c * quantity) - real_capital - sell_fee
    s_col3.error(f"**C 方案: 極限 (-{sl_c:.1f}%)**\n\n觸發價: **${sl_price_c:.2f}**\n\n淨虧: **${sl_loss_c:.2f}**\n\n**(約 RM {sl_loss_c * st.session_state.exchange_rate:.0f})**")
