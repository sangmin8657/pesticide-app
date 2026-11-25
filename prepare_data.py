import io
import os
import pandas as pd
import requests

DATA_URL = "https://github.com/sangmin8657/pesticide-app/releases/download/pesticide/pesticide_data.csv"
NIER_LOGO_URL = "https://github.com/sangmin8657/pesticide-app/releases/download/pesticide/nier_logo.png"
RDA_LOGO_URL = "https://github.com/sangmin8657/pesticide-app/releases/download/pesticide/rda_logo.png"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

os.makedirs("assets", exist_ok=True)


def download_logo(url: str, save_path: str) -> None:
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(res.content)
        print(f"로고 저장 완료: {save_path}")
    except Exception as e:
        print(f"로고 다운로드 건너뜀 ({save_path}): {e}")


def build_json_data() -> None:
    res = requests.get(DATA_URL, headers=HEADERS, timeout=30)
    res.raise_for_status()
    df = pd.read_csv(io.StringIO(res.text), dtype=str)
    df.columns = df.columns.str.strip()
    df = df.fillna("-")
    df.to_json("assets/pesticide_data.json", orient="records", force_ascii=False)
    print(f"농약 데이터 변환 완료: 총 {len(df):,}건")


if __name__ == "__main__":
    download_logo(NIER_LOGO_URL, "assets/nier_logo.png")
    download_logo(RDA_LOGO_URL, "assets/rda_logo.png")
    build_json_data()
