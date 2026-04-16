import streamlit as st

# 設定網頁標題與版面
st.set_page_config(page_title="將軍動態戰術計算機", page_icon="⚔️", layout="centered")

st.title("⚔️ 動態預算戰術計算機")
st.markdown("針對預算隨時變動設計，自動計算配股與盈虧比。")

# --- 第一區：資金與標的設定 ---
st.subheader("💰 資金與標的")
col_a, col_b = st.columns(2)

with col_a:
    ticker = st.text_input("標的代號 (Ticker)", value="INTC")
    # 這是你提到的：隨時會變動的本錢
    total_budget = st.number_input("本次投入總預算 (USD)", min_value=0.0, value=1300.0, step=10.0)

with col_b:
    buy_price = st.number_input("打算進場的價格 (USD)", min_value=0.01, value=50.0, step=0.01)
    # 固定手續費 (買1賣1)
    buy_fee = 1.0
    sell_fee = 1.0

# --- 自動配股邏輯 ---
# 計算在總預算內，扣除手續費後能買的最大股數
if buy_price > 0:
    max_quantity = int((total_budget - buy_fee) // buy_price)
else:
    max_quantity = 0

# 讓用戶可以微調股數（預設為最大股數）
quantity = st.number_input("最終確認購買股數", min_value=0, value=max_quantity, step=1)

# 計算真實投入成本
real_capital = (buy_price * quantity) + buy_fee

if quantity > 0:
    st.info(f"**實戰數據：** 投入 ${real_capital:.2f} 購買 {quantity} 股 {ticker} (剩餘閒置資金: ${total_budget - real_capital:.2f})")
else:
    st.warning("請輸入預算與價格以計算股數。")

st.divider()

# --- 第二區：自訂目標 (動態拉桿) ---
st.subheader("🎯 戰術指標設定")
t_col1, t_col2 = st.columns(2)
with t_col1:
    target_profit_usd = st.number_input("目標獲利 (USD)", value=106.0, help="預設為 RM 500")
with t_col2:
    # 讓你根據不同股票的波動性調整停損
    stop_loss_pct = st.slider("停損百分比 (%)", 1.0, 10.0, 3.0, step=0.5)

st.divider()

# --- 第三區：作戰報表 ---
if quantity > 0:
    # 獲利計算
    st.markdown(f"### 📈 {ticker} 獲利劇本")
    h_col1, h_col2 = st.columns(2)
    
    # 1. 目標達標 (RM 500 邏輯)
    tp_target_price = (real_capital + target_profit_usd + sell_fee) / quantity
    tp_target_pct = ((tp_target_price / buy_price) - 1) * 100
    h_col1.warning(f"**🎯 獲利達標 (+$ {target_profit_usd})**\n\n目標價: **${tp_target_price:.2f}**\n\n漲幅需求: **{tp_target_pct:.2f}%**")
    
    # 2. 強勢延伸 (+10% 參考)
    tp_ext_price = buy_price * 1.10
    tp_ext_profit = (tp_ext_price * quantity) - real_capital - sell_fee
    h_col2.success(f"**🚀 強勢延伸 (+10%)**\n\n目標價: **${tp_ext_price:.2f}**\n\n預計淨賺: **${tp_ext_profit:.2f}**")

    st.write("") # 留白
    
    # 停損計算
    st.markdown(f"### 📉 {ticker} 防禦劇本")
    s_col1, s_col2 = st.columns(2)
    
    # 1. 自訂停損
    sl_price = buy_price * (1 - (stop_loss_pct / 100))
    sl_loss = (sl_price * quantity) - real_capital - sell_fee
    s_col1.error(f"**🚨 自訂停損 (-{stop_loss_pct}%)**\n\n觸發價: **${sl_price:.2f}**\n\n預計虧損: **${sl_loss:.2f}**")
    
    # 2. 保命底線 (固定 -5%)
    sl_max_price = buy_price * 0.95
    sl_max_loss = (sl_max_price * quantity) - real_capital - sell_fee
    s_col2.error(f"**💀 終極底線 (-5%)**\n\n觸發價: **${sl_max_price:.2f}**\n\n預計虧損: **${sl_max_loss:.2f}**")

st.divider()
st.caption("注意事項：手續費已預設為買賣各 $1。請根據 1 小時圖 RSI 與熱錢動力決定最終扣板機時機。")