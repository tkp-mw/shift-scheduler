import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 日本語の曜日リスト
japanese_weekdays = ["月", "火", "水", "木", "金", "土", "日"]

# ユーザー入力セクション
st.title("シフト表作成ツール")

# 年と月の選択
year = st.selectbox("年を選択してください", range(2023, 2031), index=1)
month = st.selectbox("月を選択してください", range(1, 13), index=11)

# 従業員名の入力
st.markdown("### 従業員名を入力してください")
employee_names = [st.text_input(f"従業員{i+1}の名前", key=f"employee_name_{i+1}") for i in range(7)]

# 勤務タイプ選択肢
shift_types = ["", "早", "遅", "\u2716", "10-15", "10-18", "12-21", "13-21", "15-20"]

# テーブル生成ボタン
if st.button("テーブルを生成"):
    try:
        # 日付情報の計算
        start_date = datetime(year, month, 1)
        days_in_month = (datetime(year, month + 1, 1) - start_date).days if month != 12 else 31

        # テーブル作成
        dates = [start_date + timedelta(days=i) for i in range(days_in_month)]
        table_data = {
            "日付": [d.strftime("%Y-%m-%d") for d in dates],
            "曜日": [japanese_weekdays[d.weekday()] for d in dates],
            "備考": ["" for _ in dates],
        }

        # 従業員列を追加（名前が入力された場合のみ）
        for i, name in enumerate(employee_names):
            if name.strip():  # 空白の名前を無視
                table_data[f" {i+1} ({name})"] = ["" for _ in dates]

        # テーブルをセッションに保存
        st.session_state["table"] = pd.DataFrame(table_data)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# セッションからテーブルを取得して表示
if "table" in st.session_state:
    table = st.session_state["table"]

    # インタラクティブなシフト入力
    for idx, row in table.iterrows():
        st.markdown(f"#### {row['日付']} ({row['曜日']})")
        for col in table.columns[3:]:  # 従業員列のみ
            selected_shift = st.selectbox(f"{col} の勤務タイプ", shift_types, key=f"shift_{idx}_{col}")
            table.at[idx, col] = selected_shift
        table.at[idx, "備考"] = st.text_input(f"{row['日付']} の備考", value=row["備考"], key=f"remark_{idx}")

    st.session_state["table"] = table  # 更新されたテーブルを保存

    st.markdown("### スケジュールテーブル")
    st.dataframe(table)

    # スタイル付きテーブルをHTMLで表示
    st.markdown("### 印刷用スケジュール (スクリーンショット用表示)")

    # テーブルをHTML形式に変換
    def generate_html_table(dataframe):
        """DataFrameをHTMLテーブルに変換"""
        html_table = dataframe.to_html(index=False, escape=False, border=1, justify="center")
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                }}
                table {{
                    width: 90%;
                    border-collapse: collapse;
                    margin: 20px auto;
                    table-layout: fixed; /* 固定幅 */
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: center;
                    font-size: 12px; /* フォントサイズを小さく */
                    white-space: nowrap; /* 改行を防ぐ */
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                .highlight-sat {{
                    background-color: #CCFFFF; /* 薄い青 */
                    color: #0000FF;          /* 青文字 */
                }}
                .highlight-sun {{
                    background-color: #FFCCCC; /* 薄い赤 */
                    color: #FF0000;           /* 赤文字 */
                }}
                @media screen and (max-width: 768px) {{
                    table {{
                        font-size: 10px; /* モバイル用フォントサイズ */
                    }}
                }}
            </style>
        </head>
        <body>
            <h1>スケジュール表</h1>
            {html_table}
        </body>
        </html>
        """

    # 曜日に応じてスタイルを設定
    styled_table = table.copy()
    styled_table["曜日"] = styled_table["曜日"].apply(
        lambda x: f'<span class="highlight-sat">{x}</span>' if x == "土" else
                  f'<span class="highlight-sun">{x}</span>' if x == "日" else x
    )

    # HTMLを表示
    html_table = generate_html_table(styled_table)
    st.components.v1.html(html_table, height=600, scrolling=True)

