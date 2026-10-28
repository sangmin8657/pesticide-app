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
    # pandas는 .csv.gz 확장자를 자동으로 인식하여 압축 해제하며 읽어옵니다.
    df = pd.read_csv("pesticide_data.csv.gz")
    
    # 열 이름 및 텍스트 데이터의 공백 제거 (검색 오류 방지)
    df.columns = df.columns.astype(str).str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
    return df

try:
    df = load_data()

    # 필수 열 점검
    required_cols = ['작물', '병해충', '상표명', '품목명', '사용시기', '희석배수', '사용방법']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"⚠️ CSV 파일에 다음 열(컬럼)이 없습니다: {', '.join(missing_cols)}")
        st.info("💡 CSV 파일의 첫 번째 줄(제목)을 아래 이름과 동일하게 맞춰주세요:\n작물, 병해충, 카테고리, 상표명, 품목명, 사용시기, 희석배수, 사용방법")
    else:
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
                category = row.get
