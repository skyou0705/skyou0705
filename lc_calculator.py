import streamlit as st

# 設定網頁標題與版面
st.set_page_config(page_title="將軍戰術計算機", page_icon="⚔️", layout="centered")

st.title("⚔️ 戰術狙擊計算機 (ABC 完全體)")

# --- 第一區：資金與標的 ---
st.subheader("💰 資金與標的")
col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("標的代號 (Ticker)", value="TSLL")
    total_budget = st.number_input("本次投入總預算 (USD)", min_value=0.0, value=1316.0, step=10.0)
with col2:
    buy_price = st.number_input("打算進場的價格 (USD)", min_value=0.01, value=11.42, step=0.01)
    
buy_fee = 1.0
sell_fee = 1.0

# 自動計算最大股數
if buy_price > 0:
    max_quantity = int((total_budget - buy_fee) // buy_price)
else:
    max_quantity = 0

quantity = st.number_input("最終確認購買股數", min_value=0, value=max_quantity, step=1)
real_capital = (buy_price * quantity) + buy_fee

if quantity > 0:
    st.info(f"**實戰數據：** 投入 ${real_capital:.2f} 購買 {quantity} 股 {ticker} (剩餘閒置資金: ${total_budget - real_capital:.2f})")

st.divider()

# --- 第二區：雙拉桿設定 ---
st.subheader("🎯 戰術百分比 (%) 設定")
st.markdown("滑動拉桿設定你的**基準獲利**與**基準停損**，系統將自動為你生成 ABC 三套劇本。")

t_col1, t_col2 = st.columns(2)
with t_col1:
    # 獲利百分比拉桿
    target_profit_pct = st.slider("📈 基準獲利目標 (%)", min_value=1.0, max_value=30.0, value=8.0, step=0.5)
with t_col2:
    # 停損百分比拉桿 (預設2.5%，這樣ABC剛好是 2.0%, 2.5%, 3.0%)
    base_stop_loss_pct = st.slider("📉 基準停損底線 (%)", min_value=1.0, max_value=10.0, value=2.5, step=0.5)

st.divider()

# --- 第三區：作戰報表 ---
if quantity > 0:
    
    # ================= 獲利 ABC 劇本 =================
    st.markdown(f"### 📈 {ticker} 獲利劇本 (Take Profit)")
    p_col1, p_col2, p_col3 = st.columns(3)

    # A 方案: 保守 (基準減 3%，最低保底 1%)
    pct_a = max(1.0, target_profit_pct - 3.0)
    price_a = buy_price * (1 + (pct_a / 100))
    profit_a = (price_a * quantity) - real_capital - sell_fee
    p_col1.success(f"**A 方案: 保守 (+{pct_a:.1f}%)**\n\n目標價: **${price_a:.2f}**\n\n淨賺: **${profit_a:.2f}**")

    # B 方案: 達標 (基準拉桿)
    pct_b = target_profit_pct
    price_b = buy_price * (1 + (pct_b / 100))
    profit_b = (price_b * quantity) - real_capital - sell_fee
    p_col2.warning(f"**B 方案: 達標 (+{pct_b:.1f}%)**\n\n目標價: **${price_b:.2f}**\n\n淨賺: **${profit_b:.2f}**")

    # C 方案: 延伸 (基準加 3%)
    pct_c = target_profit_pct + 3.0
    price_c = buy_price * (1 + (pct_c / 100))
    profit_c = (price_c * quantity) - real_capital - sell_fee
    p_col3.success(f"**C 方案: 延伸 (+{pct_c:.1f}%)**\n\n目標價: **${price_c:.2f}**\n\n淨賺: **${profit_c:.2f}**")


    # ================= 停損 ABC 劇本 =================
    st.markdown(f"### 📉 {ticker} 防禦劇本 (Stop Loss)")
    s_col1, s_col2, s_col3 = st.columns(3)

    # 以拉桿為中心，自動生成前後 0.5% 的 ABC 劇本
    sl_b = base_stop_loss_pct
    sl_a = max(0.5, sl_b - 0.5)
    sl_c = sl_b + 0.5

    # A 方案
    sl_price_a = buy_price * (1 - (sl_a / 100))
    sl_loss_a = (sl_price_a * quantity) - real_capital - sell_fee
    s_col1.error(f"**A 方案: 撤退 (-{sl_a:.1f}%)**\n\n觸發價: **${sl_price_a:.2f}**\n\n淨虧: **${sl_loss_a:.2f}**")

    # B 方案
    sl_price_b = buy_price * (1 - (sl_b / 100))
    sl_loss_b = (sl_price_b * quantity) - real_capital - sell_fee
    s_col2.error(f"**B 方案: 標準 (-{sl_b:.1f}%)**\n\n觸發價: **${sl_price_b:.2f}**\n\n淨虧: **${sl_loss_b:.2f}**")

    # C 方案
    sl_price_c = buy_price * (1 - (sl_c / 100))
    sl_loss_c = (sl_price_c * quantity) - real_capital - sell_fee
    s_col3.error(f"**C 方案: 極限 (-{sl_c:.1f}%)**\n\n觸發價: **${sl_price_c:.2f}**\n\n淨虧: **${sl_loss_c:.2f}**")

else:
    st.caption("👈 請在上方輸入有效的買入價與預算，以解鎖戰術報表。")
