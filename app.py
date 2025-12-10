import streamlit as st
import random
import uuid
from datetime import datetime

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

# ---------------------------
# プロファイル生成
# ---------------------------
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
# セッション変数の初期化
# ---------------------------
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

if "current_round" not in st.session_state:
    st.session_state["current_round"] = 0

if "answers" not in st.session_state:
    st.session_state["answers"] = []

# ---------------------------
# ① 被験者登録ページ
# ---------------------------
if st.session_state["user_info"] is None:

    st.title("カバン選択調査 ー 被験者登録")

    with st.form("user_form"):
        age = st.number_input("年齢", min_value=10, max_value=120, step=1)
        gender = st.selectbox("性別", ["男性", "女性", "その他"])
        job = st.text_input("職業")
        submitted = st.form_submit_button("登録して調査を開始する")

    if submitted:
        st.session_state["user_info"] = {
            "id": str(uuid.uuid4()),
            "age": age,
            "gender": gender,
            "job": job,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.experimental_rerun()

    st.stop()

# ---------------------------
# ② 10回の2択調査
# ---------------------------
if st.session_state["current_round"] < 10:

    round_num = st.session_state["current_round"] + 1
    st.title(f"カバン選択調査（{round_num} / 10）")

    # ランダムプロファイル生成
    A = generate_profile()
    B = generate_profile()

    # 同一プロファイル回避
    while A == B:
        B = generate_profile()

    # 表示順もランダム
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
        return st.button(f"{label} を選ぶ")

    with col1:
        choose_left = show_profile(left_label, left_profile)

    with col2:
        choose_right = show_profile(right_label, right_profile)

    # 回答処理
    def record_answer(choice_label, choice_profile):
        st.session_state["answers"].append({
            "round": round_num,
            "choice_label": choice_label,
            "choice_profile": choice_profile,
            "A_profile": A,
            "B_profile": B,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.session_state["current_round"] += 1
        st.experimental_rerun()

    if choose_left:
        record_answer(left_label, left_profile)

    if choose_right:
        record_answer(right_label, right_profile)

    st.stop()

# ---------------------------
# ③ 完了画面
# ---------------------------
else:
    st.title("ご協力ありがとうございました！")
    st.write("以下に回答データを表示します。（保存機能は後から追加できます）")

    st.subheader("被験者情報")
    st.json(st.session_state["user_info"])

    st.subheader("回答データ（10問分）")
    st.json(st.session_state["answers"])

    st.write("このまま Google Sheets や GitHub に保存する機能を追加できます。ご希望はありますか？")
