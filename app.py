import streamlit as st
import random
import uuid
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="カバン選択調査", layout="centered")

# ---------------------------
# 属性データ
# ---------------------------
materials = ["レザー", "ナイロン", "ポリエステル"]
prices = ["1万円", "2万円", "5万円", "10万円", "20万円"]
brands = ["ナイキ", "ノースフェイス", "コーチ", "エルメス"]
discounts = ["0%", "20%", "50%", "70%"]
colors = ["黒", "白", "茶", "赤"]
bag_types = ["トート", "ボディ", "ボストン", "クラッチ", "ショルダー", "リュック", "ビジネス"]

def generate_profile():
    return {
        "素材": random.choice(materials),
        "価格": random.choice(prices),
        "ブランド": random.choice(brands),
        "割引率": random.choice(discounts),
        "色": random.choice(colors),
        "バッグ種類": random.choice(bag_types),
    }

# ---------------------------
# Google Sheets 保存関数
# ---------------------------
def save_to_google_sheets():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["sheets"]["sheet_id"]).sheet1

    header = ["round", "choice_label", "choice_profile", "A_profile", "B_profile", "timestamp"]

    # ヘッダーが無ければ追加
    if sheet.cell(1, 1).value != "round":
        sheet.append_row(header)

    # データ追加
    for ans in st.session_state.answers:
        sheet.append_row([
            ans["round"],
            ans["choice_label"],
            str(ans["choice_profile"]),
            str(ans["A_profile"]),
            str(ans["B_profile"]),
            ans["timestamp"]
        ])

    return True

# ---------------------------
# セッション初期化
# ---------------------------
if "user_info" not in st.session_state:
    st.session_state.user_info = None

if "current_round" not in st.session_state:
    st.session_state.current_round = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "current_A" not in st.session_state:
    st.session_state.current_A = None

if "current_B" not in st.session_state:
    st.session_state.current_B = None

# ---------------------------
# ① 被験者登録
# ---------------------------
if st.session_state.user_info is None:

    st.title("カバン選択調査 ー 被験者登録")

    with st.form("user_form"):
        age = st.number_input("年齢", min_value=10, max_value=120, step=1)
        gender = st.selectbox("性別", ["男性", "女性", "その他"])
        job = st.text_input("職業")
        submitted = st.form_submit_button("登録して調査を開始する")

    if submitted:
        st.session_state.user_info = {
            "id": str(uuid.uuid4()),
            "age": age,
            "gender": gender,
            "job": job,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    st.stop()

# ---------------------------
# ② 10回の2択調査
# ---------------------------
if st.session_state.current_round < 10:

    round_num = st.session_state.current_round + 1
    st.title(f"カバン選択調査（{round_num} / 10）")

    if st.session_state.current_A is None:
        A = generate_profile()
        B = generate_profile()
        while A == B:
            B = generate_profile()
        st.session_state.current_A = A
        st.session_state.current_B = B

    A = st.session_state.current_A
    B = st.session_state.current_B

    if random.random() < 0.5:
        left_label, left_profile = "A", A
        right_label, right_profile = "B", B
    else:
        left_label, left_profile = "B", B
        right_label, right_profile = "A", A

    col1, col2 = st.columns(2)

    def show_profile(label, profile):
        st.subheader(label)
        for key, val in profile.items():
            st.write(f"**{key}**：{val}")
        return st.button(f"{label} を選ぶ", key=f"btn_{label}_{round_num}")

    with col1:
        choose_left = show_profile(left_label, left_profile)

    with col2:
        choose_right = show_profile(right_label, right_profile)

    if choose_left or choose_right:

        choice_label = left_label if choose_left else right_label
        choice_profile = left_profile if choose_left else right_profile

        st.session_state.answers.append({
            "round": round_num,
            "choice_label": choice_label,
            "choice_profile": choice_profile,
            "A_profile": A,
            "B_profile": B,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        st.session_state.current_round += 1
        st.session_state.current_A = None
        st.session_state.current_B = None

    st.stop()

# ---------------------------
# ③ 完了画面
# ---------------------------
else:
    st.title("ご協力ありがとうございました！")
    st.subheader("被験者情報")
    st.json(st.session_state.user_info)

    st.subheader("回答データ（10問分）")
    st.json(st.session_state.answers)

    # ★ ここが SyntaxError の原因だった行（修正済み）
    st.write("このまま Google Sheets や GitHub に保存する機能を追加できます。ご希望はありますか？")

    if st.button("Google Sheets に保存する"):
        if save_to_google_sheets():
            st.success("Google Sheets に保存しました！")
streamlit
gspread
google-auth
google-auth-oauthlib
google-auth-httplib2
