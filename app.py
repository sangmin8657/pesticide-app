import streamlit as st
import pandas as pd

# 모바일/태블릿 화면 기본 설정
st.set_page_config(
    page_title="농약·작물보호제 현장 가이드",
    page_icon="🌱",
    layout="centered"
)

st.title("🌱 농약·작물보호제 현장 검색기")

# 엑셀(.xlsx) 파일 읽기 함수
@st.cache_data
def load_data():
    # 엑셀 파일 불러오기
    df = pd.read_excel("pesticide_data.xlsx")
    # 열 이름 및 데이터 공백 제거 (검색 오류 방지)
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
        st.error(f"⚠️ 엑셀 파일에 다음 열(컬럼)이 없습니다: {', '.join(missing_cols)}")
        st.info("💡 엑셀 첫 번째 줄(제목)을 아래 이름으로 맞춰주세요:\n작물, 병해충, 카테고리, 상표명, 품목명, 사용시기, 희석배수, 사용방법")
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
                category = row.get('카테고리', '일반')
                if pd.isna(category) or category == 'nan':
                    category = '일반'
                    
                title_text = f"💊 [{category}] {row['상표명']} ({row['품목명']})"
                
                with st.expander(title_text, expanded=True):
                    st.write(f"**· 사용 시기:** {row['사용시기']}")
                    ratio_val = row['희석배수']
                    st.write(f"**· 희석 배수:** {ratio_val}배" if pd.notna(ratio_val) else "**· 희석 배수:** 정보 없음")
                    st.write(f"**· 사용 방법:** {row['사용방법']}")

except FileNotFoundError:
    st.warning("⚠️ `pesticide_data.xlsx` 파일을 찾을 수 없습니다.")
    st.info("GitHub 저장소에 엑셀 파일을 `pesticide_data.xlsx` 이름으로 업로드했는지 확인해 주세요.")
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
