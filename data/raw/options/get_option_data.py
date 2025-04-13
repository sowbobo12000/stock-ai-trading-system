import csv
import requests
from datetime import datetime, timedelta
import time
import os

# ✅ Alpha Vantage API 키
ALPHA_VANTAGE_API_KEY = "JYBVAMGCSVCRUMMN"

# ✅ 저장할 CSV 파일명 및 필드 설정
csv_filename = "alpha_vantage_options.csv"
fieldnames = ["source", "ticker", "expiration_date", "type", "strike_price", "volume", "open_interest"]

# ✅ 기존 CSV에서 고유 키 로드 (expiration_date, ticker, strike_price, type)
def load_existing_keys():
    existing_keys = set()
    if os.path.exists(csv_filename):
        with open(csv_filename, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                key = (row["expiration_date"], row["ticker"], row["strike_price"], row['type'])
                existing_keys.add(key)
    return existing_keys

# ✅ 옵션 데이터를 Alpha Vantage에서 가져와 CSV에 저장
def fetch_and_store_alpha_vantage_options(ticker, expiration_dates):
    existing_keys = load_existing_keys()
    new_rows = []

    for exp_date in expiration_dates:
        url = f"https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol={ticker}&date={exp_date}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "data" in data:
            for option in data["data"]:
                try:
                    key = (option["expiration"], ticker, option["strike"], option["type"])
                    if key in existing_keys:
                        continue  # ✅ 이미 저장된 데이터는 건너뜀

                    row = {
                        "source": "AlphaVantage",
                        "ticker": ticker,
                        "type": option["type"],
                        "expiration_date": option["expiration"],
                        "strike_price": float(option["strike"]),
                        "volume": int(option["volume"]),
                        "open_interest": int(option["open_interest"])
                    }
                    new_rows.append(row)
                    existing_keys.add(key)  # ✅ 중복 방지를 위해 추가

                except (ValueError, KeyError):
                    continue
        else:
            print(f"❗ {exp_date} - 데이터 없음 또는 오류: {data.get('Note') or 'No data'}")

        # ✅ Alpha Vantage API Rate Limit 대응
        time.sleep(12)

    # ✅ CSV에 새 데이터 저장 (append 모드)
    if new_rows:
        write_mode = "a" if os.path.exists(csv_filename) else "w"
        with open(csv_filename, mode=write_mode, newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_mode == "w":
                writer.writeheader()
            writer.writerows(new_rows)

        print(f"✅ {len(new_rows)}개의 옵션 데이터가 '{csv_filename}'에 저장되었습니다.")
    else:
        print("📁 저장할 새로운 옵션 데이터가 없습니다.")


# ✅ 2008년 1월 1일부터 최근 N일 생성
start_date = datetime(2025, 1, 1)
end_date = datetime.today()
# max_days =   (end_date - start_date).days + 1
max_days= 80
expiration_dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(max_days)]

# ✅ 실행
ticker = "SPY"
fetch_and_store_alpha_vantage_options(ticker, expiration_dates)
