import streamlit as st
import pandas as pd

# 모바일/태블릿 화면 기본 설정
st.set_page_config(
    page_title="농약·작물보호제 현장 가이드",
    page_icon="🌱",
    layout="centered"
)

st.title("🌱 농약·작물보호제 현장 검색기")

# Gzip 압축된 CSV 파일(.csv.gz) 읽기 함수
@st.cache_data
def load_data():
    df = pd.read_csv("pesticide_data.csv.gz")
    # 열 이름 및 데이터의 앞뒤 공백 제거
    df.columns = df.columns.astype(str).str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
    return df

# 앱 실행 영역
try:
    df = load_data()

    # 1. 작물 선택 드롭다운
    crop_list = sorted(df['작물'].dropna().unique())
    col1, col2 = st.columns(2)
    
    with col1:
        selected_crop = st.selectbox("1. 작물 선택", crop_list)

    # 2. 해당 작물의 병해충 선택 드롭다운
    filtered_by_crop = df[df['작물'] == selected_crop]
    disease_list = sorted(filtered_by_crop['병해충'].dropna().unique())
    
    with col2:
        selected_disease = st.selectbox("2. 병해충 선택", disease_list)

    # 3. 검색 결과 출력
    results = filtered_by_crop[filtered_by_crop['병해충'] == selected_disease]

    st.markdown("---")
    st.markdown(f"### 📋 검색 결과 ({len(results)}건)")

    if results.empty:
        st.warning("해당 조건에 맞는 농약 정보가 없습니다.")
    else:
        for _, row in results.iterrows():
            # 카테고리 안전 처리
            category = row['카테고리'] if '카테고리' in row and pd.notna(row['카테고리']) else '일반'
            title_text = f"💊 [{category}] {row['상표명']} ({row['품목명']})"
            
            with st.expander(title_text, expanded=True):
                st.write(f"**· 사용 시기:** {row['사용시기']}")
                ratio_val = row['희석배수'] if '희석배수' in row and pd.notna(row['희석배수']) else '정보 없음'
                st.write(f"**· 희석 배수:** {ratio_val}배")
                st.write(f"**· 사용 방법:** {row['사용방법']}")

except FileNotFoundError:
    st.warning("⚠️ `pesticide_data.csv.gz` 파일을 찾을 수 없습니다.")
    st.info("GitHub 저장소에 `pesticide_data.csv.gz` 압축 파일이 정상 업로드되었는지 확인해 주세요.")
except Exception as e:
    st.error(f"⚠️ 데이터를 불러오는 중 오류가 발생했습니다: {e}")

# 현장 희석 계산기
st.markdown("---")
st.subheader("🧮 현장 희석 계산기")
col_tank, col_ratio = st.columns(2)
with col_tank:
    tank_capacity = st.number_input("약통 용량 (L)", value=20.0, step=5.0)
with col_ratio:
    ratio = st.number_input("희석 배수", value=2000, step=100)

if ratio > 0:
    required_amount = (tank_capacity * 1000) / ratio
    st.success(f"💡 **필요 약제량:** 약 **{required_amount:.1f} mL (g)**")
