import streamlit as st
import pandas as pd

# 1. 페이지 레이아웃 및 타이틀 설정
st.set_page_config(
    page_title="농약 안전사용 및 적용병해충 검색 시스템",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. GitHub Release 데이터 로딩 함수 (캐싱 적용)
# GitHub Release의 Direct Download URL을 입력합니다.
DATA_URL = "https://github.com/sangmin8657/pesticide-app/releases/download/v1.0.0/pesticide_data.csv"

@st.cache_data(ttl=86400, show_spinner="대용량 농약 데이터를 로딩하는 중입니다...")
def load_pesticide_data(url: str) -> pd.DataFrame:
    try:
        # 모든 컬럼을 문자열 타입으로 일결 로딩하여 메모리 효율성 및 검색 정확도 확보
        df = pd.read_csv(url, dtype=str)
        df = df.fillna("-")
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 데이터 로드
df_raw = load_pesticide_data(DATA_URL)

# 3. 사이드바 - 검색 및 필터 옵션
st.sidebar.title("🔍 농약 검색 필터")

if df_raw.empty:
    st.warning("데이터를 불러오지 못했습니다. GITHUB_RELEASE_URL을 확인해주세요.")
    st.stop()

# (1) GITHUB Release URL 직접 수정 기능 (테스트용)
with st.sidebar.expander("⚙️ 데이터 출처 설정"):
    custom_url = st.text_input("GitHub Release CSV URL", value=DATA_URL)
    if custom_url != DATA_URL:
        DATA_URL = custom_url
        st.cache_data.clear()
        st.rerun()

# (2) 용도 필터
use_categories = ["전체"] + sorted([x for x in df_raw["용도"].unique() if x != "-"])
selected_use = st.sidebar.selectbox("1. 용도 선택", use_categories)

# 용도 1차 필터링
df_filtered = df_raw.copy()
if selected_use != "전체":
    df_filtered = df_filtered[df_filtered["용도"] == selected_use]

# (3) 작물명 검색 및 선택
all_crops = sorted([x for x in df_filtered["작물명"].unique() if x != "-"])
selected_crop = st.sidebar.selectbox("2. 작물명 선택 (선택 또는 검색)", ["전체"] + all_crops)

if selected_crop != "전체":
    df_filtered = df_filtered[df_filtered["작물명"] == selected_crop]

# (4) 적용병해충 선택
all_pests = sorted([x for x in df_filtered["적용병해충"].unique() if x != "-"])
selected_pest = st.sidebar.selectbox("3. 적용 병해충 선택", ["전체"] + all_pests)

if selected_pest != "전체":
    df_filtered = df_filtered[df_filtered["적용병해충"] == selected_pest]

# (5) 상표명 / 품목명 / 일반명 키워드 검색
search_keyword = st.sidebar.text_input("4. 상표명 / 품목명 / 일반명 검색", value="")

if search_keyword.strip():
    kw = search_keyword.strip()
    df_filtered = df_filtered[
        df_filtered["상표명"].str.contains(kw, case=False, na=False) |
        df_filtered["품목명"].str.contains(kw, case=False, na=False) |
        df_filtered["일반명"].str.contains(kw, case=False, na=False)
    ]

# (6) 작용기작 필터
mechanism_list = ["전체"] + sorted([x for x in df_filtered["작용기작"].unique() if x != "-"])
selected_mechanism = st.sidebar.selectbox("5. 작용기작 선택", mechanism_list)

if selected_mechanism != "전체":
    df_filtered = df_filtered[df_filtered["작용기작"] == selected_mechanism]


# 4. 메인 화면 구성
st.title("🌾 농약 안전사용 및 적용병해충 검색 시스템")
st.caption("국립환경과학원 및 농약 등록 데이터를 기반으로 한 안전사용 기준 통합 조회 서비스")

# 요약 지표 (Metrics)
col1, col2, col3, col4 = st.columns(4)
col1.metric("검색된 등록건수", f"{len(df_filtered):,} 건")
col2.metric("대상 작물 수", f"{df_filtered['작물명'].nunique():,} 개")
col3.metric("대상 병해충 수", f"{df_filtered['적용병해충'].nunique():,} 개")
col4.metric("검색된 상표 수", f"{df_filtered['상표명'].nunique():,} 개")

st.markdown("---")

# 검색 결과 데이터프레임 출력
st.subheader("📋 검색 결과 목록")

# 주요 표시 컬럼 지정
default_columns = [
    "작물명", "적용병해충", "상표명", "품목명", "용도", "작용기작", 
    "희석배수", "사용량", "사용적기", "안전사용시기", "안전사용횟수", "회사명"
]

st.dataframe(
    df_filtered[default_columns],
    use_container_width=True,
    hide_index=True,
    height=400
)

# 데이터 다운로드 버튼
csv_data = df_filtered.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="📥 검색 결과 CSV 다운로드",
    data=csv_data,
    file_name="농약_검색결과.csv",
    mime="text/csv"
)

st.markdown("---")

# 5. 상세정보 확인 카드 (선택 품목 상세 보기)
st.subheader("🔍 품목별 상세 안전사용지침 확인")

if not df_filtered.empty:
    selected_brand = st.selectbox(
        "상세 정보를 확인할 상표명을 선택하세요:",
        options=df_filtered["상표명"].unique()
    )
    
    detail_df = df_filtered[df_filtered["상표명"] == selected_brand]
    
    for idx, row in detail_df.iterrows():
        with st.expander(f"📌 [{row['작물명']}] {row['상표명']} ({row['품목명']}) - {row['적용병해충']}", expanded=True):
            d_col1, d_col2, d_col3 = st.columns(3)
            
            with d_col1:
                st.write(f"**등록번호:** {row['등록번호']}")
                st.write(f"**구분 / 용도:** {row['구분']} / {row['용도']}")
                st.write(f"**품목명:** {row['품목명']}")
                st.write(f"**일반명(성분):** {row['일반명']} ({row['주성분함량']})")
                st.write(f"**회사명:** {row['회사명']}")
                
            with d_col2:
                st.write(f"**작물명:** {row['작물명']}")
                st.write(f"**적용병해충:** {row['적용병해충']}")
                st.write(f"**작용기작:** {row['작용기작']}")
                st.write(f"**제형:** {row['제형']}")
                st.write(f"**등록일:** {row['등록일']}")

            with d_col3:
                st.write(f"**희석배수:** {row['희석배수']}")
                st.write(f"**사용량:** {row['사용량']}")
                st.write(f"**사용적기:** {row['사용적기']}")
                st.write(f"**안전사용시기:** {row['안전사용시기']}")
                st.write(f"**안전사용횟수:** {row['안전사용횟수']}")
                st.write(f"**독성 (인축/어독성):** {row['인축독성']} / {row['어독성']}")
                st.write(f"**사용방법:** {row['사용방법']}")
else:
    st.info("검색 조건에 해당하는 데이터가 없습니다.")
