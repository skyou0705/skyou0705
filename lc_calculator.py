import streamlit as st
import yfinance as yf

# 設定網頁標題與版面
st.set_page_config(page_title="戰術計算機", page_icon="⚔️", layout="centered")

# --- 匯率與預算雙向連動邏輯 (Session State) ---
# 確保系統記得你的預算和匯率
if 'usd_budget' not in st.session_state:
    st.session_state.usd_budget = 1316.0
if 'exchange_rate' not in st.session_state:
    st.session_state.exchange_rate = 4.75
if 'myr_budget' not in st.session_state:
    st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate

# 當美金預算改變時，自動算馬幣
def update_myr():
    st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate

# 當馬幣預算改變時，自動算美金
def update_usd():
    st.session_state.usd_budget = st.session_state.myr_budget / st.session_state.exchange_rate

# 當匯率改變時，以美金為主更新馬幣
def update_rate():
    st.session_state.myr_budget = st.session_state.usd_budget * st.session_state.exchange_rate


st.title("⚔️ 戰術狙擊計算機")
st.caption("版本：自動抓價 + 雙幣匯率連動")

# --- 第一區：資金與標的 ---
st.subheader("💰 資金與標的")

# 1. 匯率設定
st.number_input("🔄 美金/馬幣 即時匯率 (USD/MYR)", min_value=3.0, max_value=6.0, step=0.01, 
                key="exchange_rate", on_change=update_rate, help="預設為 4.75，可根據銀行實際匯率微調")

col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("標的代號 (Ticker)", value="TSLL").upper()

with col2:
    st.number_input("投入總預算 (USD)", min_value=0.0, step=10.0, 
                    key="usd_budget", on_change=update_myr)

with col3:
    st.number_input("投入總預算 (MYR)", min_value=0.0, step=50.0, 
                    key="myr_budget", on_change=update_usd)

# 統一使用換算後的美金作為運算基礎
total_budget = st.session_state.usd_budget

# 啟動自動抓價雷達
current_price = 0.00
if ticker:
    try:
        stock_info = yf.Ticker(ticker)
        current_price = stock_info.fast_info.last_price
    except Exception:
        current_price = 0.00

col4, col5 = st.columns(2)
with col4:
    buy_price = st.number_input("打算進場的價格 (USD)", min_value=0.01, 
                                value=float(current_price) if current_price > 0 else 11.42, 
                                step=0.01, help="已自動抓取最新市價，可手動微調。")

buy_fee = 1.0
sell_fee = 1.0

# 自動計算最大股數
if buy_price > 0:
    max_quantity = int((total_budget - buy_fee) // buy_price)
else:
    max_quantity = 0

with col5:
    quantity = st.number_input("最終確認購買股數", min_value=0, value=max_quantity, step=1)
    
real_capital = (buy_price * quantity) + buy_fee

if quantity > 0:
    st.info(f"**實戰數據：** 投入 **${real_capital:.2f} USD** (約 RM {real_capital * st.session_state.exchange_rate:.2f}) 購買 **{quantity}** 股 {ticker}。 \n\n 剩餘閒置資金: ${total_budget - real_capital:.2f} USD")

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

else:
    st.caption("👈 請在上方輸入有效的買入價與預算，以解鎖戰術報表。")
