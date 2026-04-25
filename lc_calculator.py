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
    "zh-cn": { ... },  # 簡中內容與之前相同
    "en": { ... }      # 英文內容與之前相同
}

lang = st.session_state.language

# ==================== 新增：音量條風格 CSS ====================
st.markdown("""
<style>
    .big-title { font-size: 2.45rem !important; font-weight: 700; background: linear-gradient(90deg, #FFD700, #FFAA00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.3rem; letter-spacing: -0.5px; }
    .execution-data { font-size: 0.98rem !important; line-height: 1.75; }
    
    /* === 通用 Slider 美化 === */
    div[data-baseweb="slider"] {
        padding: 20px 0 10px 0 !important;
    }
    /* 軌道底色 */
    div[data-baseweb="slider"] > div > div > div:nth-child(2) {
        background: #333 !important;
        height: 8px !important;
        border-radius: 9999px !important;
    }
    /* 填充顏色 - 左邊獲利 (綠色音量條) */
    div[data-baseweb="slider"]:nth-of-type(1) > div > div > div:first-child {
        background: linear-gradient(90deg, #00ff9d, #00cc7a) !important;
        box-shadow: 0 0 12px rgba(0, 255, 157, 0.6) !important;
    }
    /* 填充顏色 - 右邊停損 (紅色音量條) */
    div[data-baseweb="slider"]:nth-of-type(2) > div > div > div:first-child {
        background: linear-gradient(90deg, #ff4d4d, #e60000) !important;
        box-shadow: 0 0 12px rgba(255, 77, 77, 0.7) !important;
    }
    /* 滑塊 (Thumb) */
    div[data-baseweb="slider"] div[role="slider"] {
        background: #ffffff !important;
        box-shadow: 0 0 10px rgba(255,255,255,0.8) !important;
        width: 20px !important;
        height: 20px !important;
        border: 2px solid #111 !important;
    }
    /* 刻度線強化 */
    div[data-baseweb="slider"] div[role="slider"] ~ div::after {
        content: '';
        position: absolute;
        height: 100%;
        width: 100%;
        background: repeating-linear-gradient(
            90deg,
            transparent,
            transparent 9.5%,
            rgba(255,255,255,0.3) 9.5%,
            rgba(255,255,255,0.3) 10.5%
        );
    }
    
    .stApp { background-color: #0E1117; }
</style>
""", unsafe_allow_html=True)

# ==================== 右上角語言按鈕 + 其他功能（與上一個版本完全相同） ====================
# （這裡直接貼你上一個版本從 header_cols 到 實行數據 的完整程式碼，我不重複貼以免你混亂）

# ...（請保留你目前檔案中從 header_cols 到 實行數據 的所有程式碼）...

# ==================== 戰術百分比設定 ====================
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

cents_mode = st.toggle(trans[lang]["cents_toggle"], value=False, key="cents_mode")

st.divider()

# ==================== 後面獲利/停損劇本 + disclaimer（不變） ====================
# （直接使用你上一個版本的完整劇本程式碼即可）
