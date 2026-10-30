import base64
import io
import os
import pandas as pd
import requests
import streamlit as st

# ==========================================
# 0. GitHub Release URL 설정 및 로고 파일 로딩
# ==========================================
DATA_URL = "https://github.com/sangmin8657/pesticide-app/releases/download/pesticide/pesticide_data.csv"
NIER_LOGO_URL = "https://github.com/sangmin8657/pesticide-app/releases/download/pesticide/nier_logo.png"


@st.cache_resource
def get_image_base64_from_url(url: str) -> str:
    """웹 URL의 이미지 파일을 읽어 Base64 문자열로 변환하는 함수"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return base64.b64encode(res.content).decode()
    except Exception:
        return ""


# 로고 이미지 Base64 인코딩 데이터 생성
nier_logo_b64 = get_image_base64_from_url(NIER_LOGO_URL)


# 1. 페이지 레이아웃 및 타이틀 설정
st.set_page_config(
    page_title="골프장 농약 안전사용 도우미",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 모바일 대응 CSS & 하단 출처(Footer) 스타일링
st.markdown(
    """
    <style>
    /* 1. 메인 헤더 & 타이틀 반응형 스타일 (모바일 화면 이탈 방지 최적화) */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between; /* 타이틀 좌측, 로고 우측 정렬 */
        gap: 10px;
        margin-bottom: 1rem;
        width: 100%;
    }
    .header-logo {
        height: 48px;
        max-width: 35%;
        object-fit: contain;
        flex-shrink: 0; /* 로고 형태 및 비율 보존 */
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1b4332;
        white-space: nowrap;
        margin: 0;
    }

    /* 📱 모바일 전용 반응형 헤더 스타일 (600px 이하) */
    @media (max-width: 600px) {
        .header-container {
            gap: 4px;
        }
        .header-logo {
            height: 24px !important; /* 모바일 환경 로고 사이즈 축소 */
            max-width: 30% !important;
        }
        .main-title {
            font-size: 0.95rem !important; /* 모바일 환경 타이틀 크기 및 자간 최적화 */
            letter-spacing: -0.8px !important;
        }
    }
    
    /* 2. 모바일 가로 1줄 요약지표 스타일 */
    .metric-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #f8f9fa;
        padding: 10px 6px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    .metric-box {
        flex: 1;
        text-align: center;
        padding: 2px;
    }
    .metric-box:not(:last-child) {
        border-right: 1px solid #dee2e6;
    }
    .metric-label {
        font-size: 11px;
        color: #6c757d;
        margin-bottom: 3px;
        white-space: nowrap;
    }
    .metric-value {
        font-size: 14px;
        font-weight: bold;
        color: #1b4332;
        white-space: nowrap;
    }

    /* 3. 푸터(Footer) 데이터 출처 영역 스타일 */
    .footer-container {
        margin-top: 50px;
        padding: 20px 15px;
        background-color: #f8f9fa;
        border-top: 2px solid #2d6a4f;
        border-radius: 8px;
        font-size: 12px;
        color: #495057;
    }
    .footer-logos {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }
    .footer-nier-logo {
        height: 32px;
        object-fit: contain;
        vertical-align: middle;
    }
    .agency-badge {
        display: inline-block;
        padding: 4px 9px;
        background-color: #e9ecef;
        color: #212529;
        border-radius: 4px;
        font-weight: 600;
        font-size: 11px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 2. 데이터 로딩 및 필터 옵션 추출 캐싱 함수
@st.cache_data(show_spinner="대용량 농약 데이터를 로딩하는 중입니다...")
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


@st.cache_data
def get_unique_options(df: pd.DataFrame, column_name: str) -> list:
    """드롭다운 옵션 추출 연산 캐싱"""
    if column_name in df.columns:
        return sorted([x for x in df[column_name].unique() if x != "-"])
    return []


df_raw = load_pesticide_data(DATA_URL)

if df_raw.empty:
    st.warning(
        "데이터를 불러오지 못했습니다. GITHUB Release URL 및 저장소 공개 상태를"
        " 확인해주세요."
    )
    st.stop()

# 메인 헤더 영역 (타이틀 좌측, 국립환경과학원 로고 우측)
if nier_logo_b64:
    header_html = f"""
    <div class="header-container">
        <h1 class="main-title">⛳ 골프장 농약 안전사용 도우미</h1>
        <img src="data:image/png;base64,{nier_logo_b64}" class="header-logo" alt="국립환경과학원 로고">
    </div>
    """
else:
    header_html = '<h1 class="main-title">⛳ 골프장 농약 안전사용 도우미</h1>'

st.markdown(header_html, unsafe_allow_html=True)

# 3. 메인 탭 구성
tab1, tab2 = st.tabs(["🔍 농약 검색", "🧪 희석배수 계산기"])

# ==========================================
# TAB 1: 농약 검색
# ==========================================
with tab1:
    # (1) 상단 검색 필터
    with st.container(border=True):
        st.subheader("🔍 농약 검색 조건")

        col_filter1, col_filter2, col_filter3 = st.columns(3)

        # 1. 용도 선택
        with col_filter1:
            use_categories = ["전체"] + get_unique_options(df_raw, "용도")
            selected_use = st.selectbox("1. 용도 선택", use_categories)

        # 1차 필터링 (용도)
        df_step1 = df_raw.copy()
        if selected_use != "전체":
            df_step1 = df_step1[df_step1["용도"] == selected_use]

        # 2. 작물 선택
        with col_filter2:
            all_crops = get_unique_options(df_step1, "작물명")
            selected_crop = st.selectbox("2. 작물 선택", ["전체"] + all_crops)

        # 2차 필터링 (작물)
        df_step2 = df_step1.copy()
        if selected_crop != "전체":
            df_step2 = df_step2[df_step2["작물명"] == selected_crop]

        # 3. 적용 병해충 선택
        with col_filter3:
            all_pests = get_unique_options(df_step2, "적용병해충")
            selected_pest = st.selectbox(
                "3. 적용 병해충 선택", ["전체"] + all_pests
            )

        # 3차 필터링 (병해충)
        df_step3 = df_step2.copy()
        if selected_pest != "전체":
            df_step3 = df_step3[df_step3["적용병해충"] == selected_pest]

        # 4. 키워드 검색
        search_keyword = st.text_input(
            "4. 상표명 / 품목명 / 성분명 키워드 검색",
            value="",
            placeholder="검색어를 입력하세요 (예: 가가방, XXX 수화제, 가스가마이신 등)",
        )

    # 최종 필터링 데이터 적용
    df_filtered = df_step3.copy()

    if search_keyword.strip():
        kw = search_keyword.strip()
        df_filtered = df_filtered[
            df_filtered["상표명"].str.contains(kw, case=False, na=False)
            | df_filtered["품목명"].str.contains(kw, case=False, na=False)
            | df_filtered["일반명"].str.contains(kw, case=False, na=False)
        ]

    # (2) 검색 결과 요약 지표 (모바일 가로 1줄 배치)
    st.markdown(
        f"""
    <div class="metric-container">
        <div class="metric-box">
            <div class="metric-label">검색 결과</div>
            <div class="metric-value">{len(df_filtered):,} 건</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">대상 작물</div>
            <div class="metric-value">{df_filtered['작물명'].nunique():,} 개</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">대상 병해충</div>
            <div class="metric-value">{df_filtered['적용병해충'].nunique():,} 개</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">검색 상표수</div>
            <div class="metric-value">{df_filtered['상표명'].nunique():,} 개</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

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
            f" **{MAX_DISPLAY}건**만 표에 표시합니다. 상단에서 작물이나 병해충을"
            " 선택하시면 상세한 조회가 가능합니다."
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
            lambda r: (
                f"[{r['상표명']}] {r['작물명']} - {r['적용병해충']}"
                f" ({r['회사명']})"
            ),
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
                st.write(
                    f"**구분 / 용도:** {selected_row['구분']} /"
                    f" {selected_row['용도']}"
                )
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
                st.write(
                    f"**희석배수:** :blue[**{selected_row['희석배수']}**]"
                )
                st.write(f"**사용량:** {selected_row['사용량']}")
                st.write(f"**사용적기:** {selected_row['사용적기']}")
                st.write(
                    "**안전사용시기:**"
                    f" :red[**{selected_row['안전사용시기']}**]"
                )
                st.write(
                    "**안전사용횟수:**"
                    f" :red[**{selected_row['안전사용횟수']}**]"
                )
                st.write(
                    f"**독성:** 인축({selected_row['인축독성']}) /"
                    f" 어독성({selected_row['어독성']})"
                )

            st.info(f"💡 **사용방법:** {selected_row['사용방법']}")
    else:
        st.info("검색 조건에 일치하는 농약이 없습니다.")

# ==========================================
# TAB 2: 희석배수 계산기
# ==========================================
with tab2:
    st.subheader("🧪 희석배수 계산기")
    st.caption(
        "살포할 물의 양과 희석배수를 입력하면 필요한 농약 용량이 자동으로"
        " 계산됩니다."
    )

    with st.container(border=True):
        calc_col1, calc_col2, calc_col3 = st.columns(3)

        # 1. 입력단위
        with calc_col1:
            unit_type = st.radio(
                "1. 입력단위 선택",
                ["리터 (L)", "말 (1말 = 20L)"],
                horizontal=True,
            )

        # 2. 살포할 물의 양
        with calc_col2:
            if unit_type == "리터 (L)":
                water_input = st.number_input(
                    "2. 살포할 물의 양 (L)",
                    min_value=0.1,
                    value=20.0,
                    step=1.0,
                )
                water_ml = water_input * 1000.0
            else:
                mal_input = st.number_input(
                    "2. 살포할 물의 양 (말)",
                    min_value=0.1,
                    value=1.0,
                    step=0.5,
                )
                water_ml = mal_input * 20.0 * 1000.0

        # 3. 희석배수
        with calc_col3:
            dilution_ratio = st.number_input(
                "3. 희석배수 (배)",
                min_value=1,
                value=1000,
                step=100,
                help=(
                    "농약 라벨에 기재된 희석배수 숫자를 입력하세요 (예: 500,"
                    " 1000)."
                ),
            )

        # 자동 계산 결과 산출
        if dilution_ratio > 0:
            required_pesticide_ml = water_ml / dilution_ratio

            st.markdown("---")
            st.success("### 💡 자동 계산 결과")

            res1, res2 = st.columns(2)
            res1.metric(
                "필요한 물의 총량",
                f"{water_ml/1000:,.1f} L",
                f"{(water_ml/1000)/20:,.1f} 말",
            )
            res2.metric(
                "농약 용량 (자동계산)",
                f"{required_pesticide_ml:,.1f} mL (또는 g)",
            )

            st.markdown("""
            > 📌 **사용 안내**
            > * 액체 농약(액상수화제, 유제 등)은 **1mL ≒ 1g**으로 간주하여 계산됩니다.
            > * 약제를 먼저 소량의 물에 완전히 희석한 후 전체 물통에 섞으면 균일하게 혼합됩니다.
            """)


# ==========================================
# 4. 화면 최하단 출처 및 기관 표시 푸터 (Footer)
# ==========================================
nier_footer_logo_html = (
    f'<img src="data:image/png;base64,{nier_logo_b64}" class="footer-nier-logo"'
    ' alt="국립환경과학원 로고">'
    if nier_logo_b64
    else '<span class="agency-badge">국립환경과학원</span>'
)

st.markdown(
    f"""
    <div class="footer-container">
        <div class="footer-logos">
            {nier_footer_logo_html}
            <span class="agency-badge">농촌진흥청</span>
            <span class="agency-badge">농약안전정보센터</span>
        </div>
        <div>
            <strong>📢 데이터 출처 및 안내</strong><br>
            본 서비스는 <strong>농촌진흥청</strong>에서 운영하는 <strong>농약안전정보센터</strong>의 제공데이터를 활용하여 <strong>국립환경과학원</strong>에서 구축하였습니다.<br>
            <span style="color: #868e96;">※ 본 앱의 검색 결과 및 계산 결과는 토양·지하수 환경 보호 및 골프장 농약 안전사용 관리를 돕기 위한 참고 정보이며, 실제 사용 시 제품의 용기 표기 지침을 반드시 확인하시기 바랍니다.</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)
