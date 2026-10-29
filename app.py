import io
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 레이아웃 및 타이틀 설정
st.set_page_config(
    page_title="농약 안전사용 및 희석배수 계산기",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",  # 메인 화면에 집중하도록 사이드바 기본 접음
)

# GitHub Release CSV Direct Download URL
DATA_URL = "https://github.com/sangmin8657/pesticide-app/releases/download/pesticide/pesticide_data.csv"


# 2. 데이터 로딩 함수 (User-Agent 헤더 추가 및 캐싱)
@st.cache_data(
    ttl=86400, show_spinner="대용량 농약 데이터를 로딩하는 중입니다..."
)
def load_pesticide_data(url: str) -> pd.DataFrame:
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text), dtype=str)
    df = df.fillna("-")
    return df
  except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    return pd.DataFrame()


df_raw = load_pesticide_data(DATA_URL)

if df_raw.empty:
  st.warning(
      "데이터를 불러오지 못했습니다. GITHUB Release URL 및 저장소 공개 상태를"
      " 확인해주세요."
  )
  st.stop()

# 메인 타이틀
st.title("🌾 농약 안전사용 및 희석배수 계산기")

# 3. 메인 탭 구성
tab1, tab2 = st.tabs(["🔍 농약 검색 및 상세지침", "🧮 희석배수 계산기"])

# ==========================================
# TAB 1: 농약 검색 및 상세 지침
# ==========================================
with tab1:
  # (1) 첫 화면 상단 검색 필터 카드 (3컬럼 배치)
  with st.container(border=True):
    st.subheader("🔍 농약 검색 조건")

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    # 1. 용도 선택
    with col_filter1:
      use_categories = ["전체"] + sorted(
          [x for x in df_raw["용도"].unique() if x != "-"]
      )
      selected_use = st.selectbox("1. 용도 선택", use_categories)

    # 1차 필터링 (용도 기준)
    df_step1 = df_raw.copy()
    if selected_use != "전체":
      df_step1 = df_step1[df_step1["용도"] == selected_use]

    # 2. 작물명 선택 (용도 선택에 따라 동적 변경)
    with col_filter2:
      all_crops = sorted([x for x in df_step1["작물명"].unique() if x != "-"])
      selected_crop = st.selectbox("2. 작물명 선택", ["전체"] + all_crops)

    # 2차 필터링 (작물명 기준)
    df_step2 = df_step1.copy()
    if selected_crop != "전체":
      df_step2 = df_step2[df_step2["작물명"] == selected_crop]

    # 3. 적용 병해충 선택 (선택한 작물에 해당하는 병해충만 동적 노출)
    with col_filter3:
      all_pests = sorted(
          [x for x in df_step2["적용병해충"].unique() if x != "-"]
      )
      selected_pest = st.selectbox("3. 적용 병해충 선택", ["전체"] + all_pests)

    # 3차 필터링 (적용 병해충 기준)
    df_step3 = df_step2.copy()
    if selected_pest != "전체":
      df_step3 = df_step3[df_step3["적용병해충"] == selected_pest]

    # 하단 2컬럼 배치 (키워드 검색 & 작용기작)
    col_filter4, col_filter5 = st.columns(2)

    with col_filter4:
      search_keyword = st.text_input(
          "4. 상표명 / 품목명 / 성분명 키워드",
          value="",
          placeholder="검색어 입력 (예: 가가방, 수화제 등)",
      )

    with col_filter5:
      mechanism_list = ["전체"] + sorted(
          [x for x in df_step3["작용기작"].unique() if x != "-"]
      )
      selected_mechanism = st.selectbox("5. 작용기작 선택", mechanism_list)

  # 최종 필터링 데이터 적용
  df_filtered = df_step3.copy()

  if search_keyword.strip():
    kw = search_keyword.strip()
    df_filtered = df_filtered[
        df_filtered["상표명"].str.contains(kw, case=False, na=False)
        | df_filtered["품목명"].str.contains(kw, case=False, na=False)
        | df_filtered["일반명"].str.contains(kw, case=False, na=False)
    ]

  if selected_mechanism != "전체":
    df_filtered = df_filtered[df_filtered["작용기작"] == selected_mechanism]

  st.markdown("---")

  # (2) 검색 결과 요약 지표 (Metrics)
  m1, m2, m3, m4 = st.columns(4)
  m1.metric("검색 결과", f"{len(df_filtered):,} 건")
  m2.metric("대상 작물", f"{df_filtered['작물명'].nunique():,} 개")
  m3.metric("대상 병해충", f"{df_filtered['적용병해충'].nunique():,} 개")
  m4.metric("검색 상표 수", f"{df_filtered['상표명'].nunique():,} 개")

  st.markdown("---")

  # (3) 검색 결과 목록
  st.subheader("📋 검색 결과 목록")

  default_columns = [
      "작물명",
      "적용병해충",
      "상표명",
      "품목명",
      "용도",
      "작용기작",
      "희석배수",
      "사용량",
      "안전사용시기",
      "안전사용횟수",
      "회사명",
  ]

  MAX_DISPLAY = 500
  if len(df_filtered) > MAX_DISPLAY:
    st.info(
        f"💡 검색 결과가 총 **{len(df_filtered):,}건**으로 많아 상위"
        f" **{MAX_DISPLAY}건**만 표에 표시합니다. 상단 검색 조건에서 작물이나"
        " 병해충을 선택하여 결과를絞り込んでください."
    )
    display_df = df_filtered[default_columns].head(MAX_DISPLAY)
  else:
    display_df = df_filtered[default_columns]

  st.dataframe(
      display_df, use_container_width=True, hide_index=True, height=350
  )

  csv_data = df_filtered.to_csv(index=False, encoding="utf-8-sig")
  st.download_button(
      label="📥 전체 검색결과 CSV 다운로드",
      data=csv_data,
      file_name="농약_검색결과.csv",
      mime="text/csv",
  )

  st.markdown("---")

  # (4) 상세 안전사용지침 카드
  st.subheader("🔎 검색된 농약 상세 안전사용지침")

  if not df_filtered.empty:
    df_filtered_copy = df_filtered.copy()
    df_filtered_copy["select_label"] = df_filtered_copy.apply(
        lambda r: f"[{r['상표명']}] {r['작물명']} - {r['적용병해충']} ({r['회사명']})",
        axis=1,
    )

    options_list = list(
        dict.fromkeys(df_filtered_copy["select_label"].tolist())
    )

    selected_label = st.selectbox(
        "상세 지침을 확인할 농약을 선택하세요 (현재 검색 결과 목록 내 품목):",
        options=options_list,
    )

    selected_row = df_filtered_copy[
        df_filtered_copy["select_label"] == selected_label
    ].iloc[0]

    with st.container(border=True):
      st.markdown(
          f"### 📌 [{selected_row['작물명']}] {selected_row['상표명']}"
          f" ({selected_row['품목명']})"
      )

      d_col1, d_col2, d_col3 = st.columns(3)

      with d_col1:
        st.write(f"**등록번호:** {selected_row['등록번호']}")
        st.write(f"**구분 / 용도:** {selected_row['구분']} / {selected_row['용도']}")
        st.write(f"**품목명:** {selected_row['품목명']}")
        st.write(
            f"**성분(일반명):** {selected_row['일반명']}"
            f" ({selected_row['주성분함량']})"
        )
        st.write(f"**제조사:** {selected_row['회사명']}")

      with d_col2:
        st.write(f"**적용 작물:** {selected_row['작물명']}")
        st.write(f"**적용 병해충:** {selected_row['적용병해충']}")
        st.write(f"**작용기작:** {selected_row['작용기작']}")
        st.write(f"**제형:** {selected_row['제형']}")
        st.write(f"**등록일자:** {selected_row['등록일']}")

      with d_col3:
        st.write(f"**희석배수:** :blue[**{selected_row['희석배수']}**]")
        st.write(f"**사용량:** {selected_row['사용량']}")
        st.write(f"**사용적기:** {selected_row['사용적기']}")
        st.write(f"**안전사용시기:** :red[**{selected_row['안전사용시기']}**]")
        st.write(f"**안전사용횟수:** :red[**{selected_row['안전사용횟수']}**]")
        st.write(
            f"**독성:** 인축({selected_row['인축독성']}) /"
            f" 어독성({selected_row['어독성']})"
        )

      st.info(f"💡 **사용방법:** {selected_row['사용방법']}")
  else:
    st.info("검색 조건에 일치하는 농약이 없습니다.")

# ==========================================
# TAB 2: 희석배수 및 사용량 계산기
# ==========================================
with tab2:
  st.subheader("🧮 농약 희석배수 계산기")
  st.caption(
      "살포할 물의 양과 희석배수를 입력하여 필요한 약제(농약)의 정량을"
      " 계산합니다."
  )

  calc_col1, calc_col2 = st.columns(2)

  with calc_col1:
    unit_type = st.radio(
        "물의 양 입력 단위 선택",
        ["리터 (L)", "말 (1말 = 20L)"],
        horizontal=True,
    )

    if unit_type == "리터 (L)":
      water_input = st.number_input(
          "살포할 물의 양 (L)", min_value=0.1, value=20.0, step=1.0
      )
      water_ml = water_input * 1000.0
    else:
      mal_input = st.number_input(
          "살포할 물의 양 (말)", min_value=0.1, value=1.0, step=0.5
      )
      water_ml = mal_input * 20.0 * 1000.0

  with calc_col2:
    dilution_ratio = st.number_input(
        "희석 배수 (예: 500배, 1000배)",
        min_value=1,
        value=1000,
        step=100,
        help="농약 포장지에 기재된 희석배수를 입력하세요.",
    )

    cap_size = st.number_input(
        "농약 뚜껑(캡) 용량 (mL) [선택사항]",
        min_value=1.0,
        value=20.0,
        step=5.0,
        help="뚜껑 기준 정량을 측정할 때 사용합니다. (보통 20mL)",
    )

  if dilution_ratio > 0:
    required_pesticide_ml = water_ml / dilution_ratio
    cap_count = required_pesticide_ml / cap_size

    st.success("### 💡 계산 결과")

    res_c1, res_c2, res_c3 = st.columns(3)
    res_c1.metric(
        "필요한 물의 총량",
        f"{water_ml/1000:,.1f} L",
        f"{(water_ml/1000)/20:,.1f} 말",
    )
    res_c2.metric("필요 약제(농약) 용량", f"{required_pesticide_ml:,.1f} mL (또는 g)")
    res_c3.metric(
        "뚜껑(캡) 기준 약제량",
        f"약 {cap_count:,.1f} 뚜껑",
        f"1뚜껑당 {cap_size}mL 기준",
    )

    st.markdown("""
        > 📌 **참고 및 주의사항**
        > * 액상 수화제, 유제 등 액체 농약의 경우 **1mL ≒ 1g**으로 계산됩니다.
        > * 수화제(가루) 농약의 경우 저울을 이용해 g 단위를 측정하는 것이 가장 정확합니다.
        > * 약제를 먼저 물 소량에 완전히 녹인 후 잔여 물을 채워 혼합하시면 균일하게 희석됩니다.
        """)
