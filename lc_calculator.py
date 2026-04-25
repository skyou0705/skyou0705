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
    # zh-cn 和 en 的 trans 字典與之前完全相同（這裡省略以節省篇幅，請保留你上一個版本的內容）
    "zh-cn": { ... },
    "en": { ... }
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

# ==================== 功能區塊（匯率、平台、資金、股價、股數、實行數據）全部不變 ====================
# （這裡與上一個版本完全相同，請直接保留你上一個版本從 @st.cache_data 到 實行數據 的程式碼）

# ...（省略中間不變的部分，直接貼上你上一個版本的內容即可）

# ==================== 戰術百分比設定（新增仙位顯示 Toggle） ====================
st.subheader(trans[lang]["percent_title"])
t_col1, t_col2 = st.columns(2)

with t_col1:
    target_profit_pct = st.slider(trans[lang]["profit_slider"], 1.0, 200.0, 3.0, step=1.0)
    st.markdown('''
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#999; margin:-8px 0 12px 0; padding:0 8px; border-bottom:1px solid #333;">
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

# 新增：仙位顯示 Toggle（iPhone 風格）
cents_mode = st.toggle(trans[lang].get("cents_toggle", "仙位顯示"), value=False, key="cents_mode")

st.divider()

# ==================== 獲利 / 停損劇本（新增精度控制） ====================
def format_price(price, cents_mode):
    if cents_mode:
        return f"${price:.4f}"
    else:
        return f"${price:.2f}"

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

    # 防禦劇本
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
