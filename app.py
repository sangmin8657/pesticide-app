import streamlit as st
import pandas as pd
import io

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="농약 등록 정보 검색 시스템",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 데이터 로드 함수 (캐싱 및 인코딩 예외 처리)
@st.cache_data(show_spinner="농약 등록 데이터를 불러오는 중입니다...")
def load_pesticide_data(file_path):
    encodings = ['cp949', 'euc-kr', 'utf-8-sig', 'utf-8']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        st.error("CSV 파일 인코딩을 읽을 수 없습니다. 파일 상태를 확인해 주세요.")
        return pd.DataFrame()
    
    # 결측치 기본값 채우기
    fill_cols = ['작용기작', '희석배수', '안전사용시기', '안전사용횟수']
    for col in fill_cols:
        if col in df.columns:
            df[col] = df[col].fillna('-')
            
    return df

# 데이터 불러오기
df_raw = load_pesticide_data('pesticide_data.csv')

# 3. 사이드바 - 검색 및 필터링 옵션
st.sidebar.header("🔍 농약 검색 필터")

if not df_raw.empty:
    # 3-1. 작물명 선택
    crop_list = ["전체"] + sorted(list(df_raw['작물명'].dropna().unique()))
    selected_crop = st.sidebar.selectbox("1. 작물명 선택", crop_list, index=0)

    # 선택된 작물에 따라 적용병해충 목록 동적 필터링
    if selected_crop != "전체":
        filtered_pests = df_raw[df_raw['작물명'] == selected_crop]['적용병해충'].dropna().unique()
    else:
        filtered_pests = df_raw['적용병해충'].dropna().unique()

    # 3-2. 적용병해충 선택
    pest_list = ["전체"] + sorted(list(filtered_pests))
    selected_pest = st.sidebar.selectbox("2. 적용 병해충 선택", pest_list, index=0)

    # 3-3. 농약 용도 선택 (살균, 살충, 제초 등)
    purpose_list = sorted(list(df_raw['용도'].dropna().unique()))
    selected_purposes = st.sidebar.multiselect("3. 용도 선택 (복수 선택 가능)", purpose_list, default=[])

    # 3-4. 통합 검색어 (상표명 / 품목명 / 일반명 / 회사명)
    search_keyword = st.sidebar.text_input("4. 상표명 / 품목명 / 회사명 검색", placeholder="예: 가가방, 만코제브, 이엑스아이디")

    # 4. 데이터 필터링 로직
    df_filtered = df_raw.copy()

    if selected_crop != "전체":
        df_filtered = df_filtered[df_filtered['작물명'] == selected_crop]

    if selected_pest != "전체":
        df_filtered = df_filtered[df_filtered['적용병해충'] == selected_pest]

    if selected_purposes:
        df_filtered = df_filtered[df_filtered['용도'].isin(selected_purposes)]

    if search_keyword.strip():
        kw = search_keyword.strip()
        mask = (
            df_filtered['상표명'].astype(str).str.contains(kw, case=False, na=False) |
            df_filtered['품목명'].astype(str).str.contains(kw, case=False, na=False) |
            df_filtered['일반명'].astype(str).str.contains(kw, case=False, na=False) |
            df_filtered['회사명'].astype(str).str.contains(kw, case=False, na=False)
        )
        df_filtered = df_filtered[mask]

    # 5. 메인 화면 구성
    st.title("🌿 작물별 농약 등록 정보 검색 시스템")
    st.caption("국가 등록 농약 데이터를 기반으로 작물, 병해충, 상표별 안전사용 기준 및 처방 정보를 조회합니다.")

    # 대시보드 요약 지표
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("검색된 등록 건수", f"{len(df_filtered):,} 건")
    with col2:
        st.metric("대상 작물 수", f"{df_filtered['작물명'].nunique():,} 개")
    with col3:
        st.metric("관련 병해충 수", f"{df_filtered['적용병해충'].nunique():,} 종")
    with col4:
        st.metric("해당 상표 수", f"{df_filtered['상표명'].nunique():,} 개")

    st.markdown("---")

    # 6. 검색 결과 데이터 테이블
    st.subheader("📋 농약 등록 목록")
    
    # 기본 표시 컬럼 설정
    display_cols = [
        '작물명', '적용병해충', '상표명', '품목명', '용도', 
        '작용기작', '희석배수', '사용량', '안전사용시기', '안전사용횟수', '회사명'
    ]
    
    st.dataframe(
        df_filtered[display_cols],
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # 7. 상세 정보 조회 및 CSV 다운로드
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🔍 상세 정보 조회")
        if not df_filtered.empty:
            selected_idx = st.selectbox(
                "상세 정보를 확인할 품목을 선택하세요:",
                options=df_filtered.index,
                format_func=lambda x: f"[{df_filtered.loc[x, '작물명']}] {df_filtered.loc[x, '상표명']} ({df_filtered.loc[x, '품목명']}) - {df_filtered.loc[x, '회사명']}"
            )
            
            detail = df_filtered.loc[selected_idx]
            
            with st.expander("📌 세부 처방 및 독성 정보 보기", expanded=True):
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.write(f"**등록번호:** {detail['등록번호']}")
                    st.write(f"**작물명 / 적용병해충:** {detail['작물명']} / {detail['적용병해충']}")
                    st.write(f"**상표명 / 품목명:** {detail['상표명']} / {detail['품목명']}")
                    st.write(f"**일반명 / 주성분함량:** {detail['일반명']} ({detail['주성분함량']})")
                    st.write(f"**제형 / 용도:** {detail['제형']} / {detail['용도']}")
                    st.write(f"**작용기작:** {detail['작용기작']}")
                with d_col2:
                    st.write(f"**희석배수 / 사용량:** {detail['희석배수']} / {detail['사용량']}")
                    st.write(f"**사용적기:** {detail['사용적기']}")
                    st.write(f"**사용방법:** {detail['사용방법']}")
                    st.write(f"**안전사용시기:** {detail['안전사용시기']}")
                    st.write(f"**안전사용횟수:** {detail['안전사용횟수']}")
                    st.write(f"**인축독성 / 어독성:** {detail['인축독성']} / {detail['어독성']}")
                    st.write(f"**제조/수입사:** {detail['회사명']}")

    with col_right:
        st.subheader("📥 검색 결과 다운로드")
        st.write("현재 필터링된 결과를 CSV 파일로 추출합니다.")
        
        # 엑셀 깨짐 방지를 위한 UTF-8-SIG 인코딩 처리
        csv_data = df_filtered.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        
        st.download_button(
            label="📄 CSV 파일 다운로드",
            data=csv_data,
            file_name="pesticide_search_result.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.error("데이터 파일(`pesticide_data.csv`)을 찾을 수 없거나 데이터가 비어 있습니다.")
