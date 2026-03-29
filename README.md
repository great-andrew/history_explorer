# 🌍 History Explorer

> AI가 역사적 사건의 동시대성을 3D 지구본 위에서 시각적으로 보여주는 교육 웹앱

---

## 개요

**History Explorer**는 하나의 역사적 사건을 입력하면, 같은 시대에 세계 각국에서 어떤 일이 일어났는지를 3D 지구본 위의 카드와 AI 음성 나레이션으로 보여주는 로컬 AI 교육 앱입니다.

예를 들어 *"영국 산업혁명"*을 검색하면, 같은 시기 조선, 일본, 프랑스에서 무슨 일이 있었는지를 지구본 위에서 동시에 탐험할 수 있습니다.

---

## 주요 기능

- 🔍 **자연어 히스토리 검색** — 한국어/영어 쿼리 모두 지원
- 🌐 **3D 지구본 시각화** — react-globe.gl 기반, 나라별 이벤트 카드 표시
- 🤖 **AI 컨텐츠 생성** — LangGraph 파이프라인으로 나라별 역사 컨텐츠 병렬 생성
- 🎙️ **AI 음성 나레이션** — Kokoro TTS로 각 카드 내용을 음성으로 읽어줌
- 📚 **RAG 기반 검색** — 한국사는 로컬 DB, 해외는 Wikipedia API 활용
- ⚡ **완전 로컬 실행** — 외부 API 없이 MacBook에서 동작

---

## 시스템 아키텍처

```
사용자 쿼리
     ↓
┌─────────────────────────────────────┐
│         LangGraph Pipeline          │
│                                     │
│  input_validator                    │
│       ↓                             │
│  scope_limiter                      │
│  (나라별 쿼리 분리)                  │
│       ↓                             │
│  content_generator × N (병렬)       │
│  ├─ Korea  → RAG (ChromaDB)         │
│  ├─ UK     → Wikipedia API          │
│  └─ Japan  → Wikipedia API          │
│       ↓                             │
│  output_assembler                   │
└─────────────────────────────────────┘
     ↓
FastAPI + WebSocket
     ↓
React Frontend
├── react-globe.gl (3D 지구본)
├── 나라별 이벤트 카드
└── Kokoro TTS 나레이션
```

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **LLM** | Ollama (Qwen3:8b) — 완전 로컬 |
| **오케스트레이션** | LangGraph |
| **벡터 DB** | ChromaDB + nomic-embed-text |
| **TTS** | Kokoro (82M, Apache 2.0) |
| **3D 시각화** | react-globe.gl |
| **백엔드** | FastAPI + WebSocket |
| **데이터 소스** | Wikipedia API (해외) / 로컬 PDF·TXT (한국사) |

---

## 설치 및 실행

### 사전 요구사항

- Python 3.13+
- [Ollama](https://ollama.com) 설치
- Node.js 18+

### 1. Ollama 모델 설치

```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

### 2. Python 환경 설정

```bash
git clone https://github.com/your-username/history-explorer.git
cd history-explorer

python -m venv .venv
source .venv/bin/activate

pip install -e .
```

### 3. RAG DB 구축 (최초 1회)

`docs/` 폴더에 한국사 자료(PDF 또는 TXT)를 넣고 실행:

```bash
python build_db.py
```

```
docs/
├── korea/
│   ├── joseon.pdf
│   └── modern.txt
└── global/
    └── ...
```

### 4. 앱 실행

```bash
# 백엔드
uvicorn app:app --reload

# 프론트엔드
cd frontend
npm install
npm run dev
```

---

## LangGraph 파이프라인

```
START
  └─► input_validator      # 쿼리 유효성 검사 (역사 관련 여부, 프롬프트 인젝션 방지)
        ├─► (invalid) END
        └─► scope_limiter  # 시간 범위 조정 + 나라별 쿼리 분리
              └─► content_generator × N  # 병렬 실행 (Send API)
                    └─► output_assembler
                          └─► END
```

### 노드 설명

| 노드 | 역할 |
|------|------|
| `input_validator` | 역사 쿼리 여부 판별, 프롬프트 인젝션 차단 |
| `scope_limiter` | 시간 범위 30~150년으로 조정, 나라별 쿼리 생성 |
| `content_generator` | RAG/Wikipedia로 컨텍스트 검색 후 카드 컨텐츠 생성 |
| `output_assembler` | 병렬 결과 취합 및 최종 포맷 구성 |

---

## RAG 구조

```
[최초 1회] docs/ 폴더 → PyPDFLoader/TextLoader → 청킹 → nomic-embed-text → ChromaDB 저장
[매 쿼리]  country_query → ChromaDB 유사도 검색 → 컨텍스트 → LLM
```

- 한국사 쿼리 → ChromaDB (로컬 문서)
- 해외 쿼리 → Wikipedia API → 관련 섹션 추출

---

## 프로젝트 구조

```
history-explorer/
├── build_db.py          # RAG DB 구축 스크립트 (1회 실행)
├── app.py               # LangGraph 파이프라인 + FastAPI
├── pyproject.toml
├── docs/                # 한국사 자료 (PDF/TXT)
│   └── korea/
├── chroma_db/           # ChromaDB 로컬 저장소 (자동 생성)
└── frontend/            # React 프론트엔드
    └── src/
```

---

## 개발 범위

이 프로젝트는 **6주 로컬 데모** 를 목표로 합니다.

- ✅ 단일 사용자 로컬 실행
- ✅ 외부 배포 없음
- ✅ 완전 무료 (로컬 LLM + 오픈소스)
- ❌ 멀티 유저, 클라우드 배포, 모바일 미지원

---

## 라이선스

MIT License