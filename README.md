# 부동산(아파트) 가치 분석 앱

설계 배경과 전체 로드맵은 [`DESIGN.md`](./DESIGN.md) 참고.

현재 구현 범위(Phase 1 MVP): 국토부 실거래가 수집 → DB 저장 → **가격 매력도 점수** + 시계열/% 차트.

## 구조

```
backend/    FastAPI + PostgreSQL — 국토부 수집기, 점수 엔진, API
frontend/   Next.js — 단지 검색, 시세 차트, 점수 대시보드
```

## 로컬 실행

### 1) Docker Compose로 한 번에

```bash
cp backend/.env.example backend/.env   # MOLIT_SERVICE_KEY 채우기
docker compose up --build
```

- 프론트: http://localhost:3000
- 백엔드: http://localhost:8000/docs

### 2) 개별 실행 (개발용)

**백엔드**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # DATABASE_URL, MOLIT_SERVICE_KEY 설정
PYTHONPATH=. python scripts/init_db.py
uvicorn app.main:app --reload --port 8000
```

**프론트엔드**
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

## 데이터 수집

[공공데이터포털](https://www.data.go.kr/data/15058747/openapi.do)에서 "국토교통부_아파트매매 실거래자료" 서비스키를 발급받아
`backend/.env`의 `MOLIT_SERVICE_KEY`에 설정한다.

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -m scripts.collect --ymd 202506          # 등록된 전 지역
PYTHONPATH=. python -m scripts.collect --ymd 202506 --lawd 11680  # 강남구만
```

초기 지역 범위는 서울 25개 자치구(`app/collectors/law_codes.py`). 경기/인천 등
나머지 수도권 시군구 코드는 `backend/app/collectors/law_codes_extra.csv`
(code,name 헤더)를 추가해 확장한다.

## 테스트

```bash
cd backend
source .venv/bin/activate
pytest
```

## 가격 매력도 점수

`app/scoring/price_attractiveness.py` — 전고점 대비 하락폭(60%) + 최근 거래량 추세(40%)를
0~100점으로 환산한 초기 휴리스틱. 실사용 데이터로 가중치 튜닝 필요 (`DESIGN.md` 6장 참고).
