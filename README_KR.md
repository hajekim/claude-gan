# Claude-GAN: Gemini CLI MCP 확장

**Gemini CLI가 Evaluator(Brain)로 직접 동작**하고, **Claude 4.6 Sonnet (Vertex AI)**를 MCP(Model Context Protocol) 도구로 호출하여 Generator(Hands)로 사용하는 GAN 기반 개발 시스템입니다.

## 동작 원리

```
Gemini CLI (Evaluator — 네이티브 추론)
  │
  ├─ 1. Sprint Contract(JSON DoD)를 자체 추론으로 직접 작성
  ├─ 2. claude_generate MCP 도구 호출 ──▶ Claude 4.6 Sonnet (Vertex AI)
  ├─ 3. 반환된 코드를 계약 기준으로 직접 평가
  └─ 4. Grade A 달성까지 구체적 피드백으로 반복
```

Gemini CLI의 Gemini 모델 자체가 Evaluator입니다. Claude는 서브프로세스가 아닌 MCP 도구로 호출됩니다. GAN 루프 전체가 Gemini CLI 세션 내에서 실행됩니다.

## 사전 준비 사항

- **Google Cloud Project**: Vertex AI API 활성화 및 `global` 리전에서 Claude 4.6 Sonnet 접근 권한
- **Gemini CLI**: 설치 및 인증 완료
- **Python 3.10+** 및 pip
- `gcloud auth application-default login` 완료

## 설치

### 1. 리포지토리 클론

```bash
git clone https://github.com/your-repo/claude-gan.git
cd claude-gan
```

### 2. Python 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. MCP 서버 전역 등록

`~/.gemini/settings.json`의 `mcpServers` 항목에 아래 내용을 추가합니다:

```json
{
  "mcpServers": {
    "claude-generator": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["/절대경로/claude-gan/src/mcp_server.py"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "your-gcp-project-id",
        "GOOGLE_CLOUD_LOCATION": "global",
        "PYTHONPATH": "/절대경로/claude-gan"
      }
    }
  }
}
```

`/절대경로/claude-gan`을 실제 클론한 경로로 교체하세요.

> **참고:** `python3` 경로는 `which python3`로 확인할 수 있습니다.

### 4. Evaluator 컨텍스트 로드

Evaluator 지시문을 Gemini CLI 전역 컨텍스트로 복사합니다:

```bash
cp GEMINI.md ~/.gemini/GEMINI.md
```

또는, 프로젝트 디렉토리 안에서 Gemini CLI를 실행하면 `GEMINI.md`가 자동으로 로드됩니다.

## 사용 방법

Gemini CLI를 재시작한 후 자연어로 작업을 요청합니다. GEMINI.md 지시에 따라 GAN 루프가 자동 실행됩니다:

```
Python으로 가위바위보 게임을 만들어줘. 점수 기록 기능도 포함해줘.
```

```
JWT 인증과 입력 유효성 검사가 포함된 FastAPI 서버를 구현해줘.
```

Gemini가 자동으로:
1. 자체 추론으로 Sprint Contract(DoD) 작성
2. `claude_generate` 도구로 Claude에게 구현 요청
3. 계약 기준으로 결과물 엄격 평가
4. Grade A 달성까지 구체적인 피드백으로 반복

### 결과물

| 파일 | 설명 |
|------|------|
| `artifacts/solution_SPRINT-XXX.py` | 최종 생성 코드 |
| `state/progress.json` | 스프린트 상태 및 등급 |

## 등록된 MCP 도구

전역 등록 후 모든 Gemini CLI 세션에서 사용 가능합니다:

| 도구 | 설명 |
|------|------|
| `claude_generate(task, contract, feedback)` | Claude 4.6 Sonnet (Vertex AI)으로 코드 생성/개선 |
| `save_artifact(content, filename)` | `artifacts/` 디렉토리에 결과물 저장 |
| `load_progress()` | `state/progress.json`에서 현재 스프린트 상태 로드 |
| `save_progress(sprint_id, status, grade)` | 스프린트 상태 저장 |

## 프로젝트 구조

```
claude-gan/
├── src/
│   ├── mcp_server.py        # FastMCP 서버 (stdio transport)
│   ├── tools/
│   │   └── claude_tool.py   # Claude Vertex AI 호출 핵심 로직
│   └── config.py            # 환경 변수 설정
├── tests/
│   └── test_claude_tool.py  # 단위 테스트 (TDD)
├── state/
│   └── progress.json        # 스프린트 상태 영속성
├── artifacts/               # 생성 코드 출력
├── GEMINI.md                # Gemini CLI용 Evaluator 지시문
├── gemini-extension.json    # Extension 매니페스트
└── requirements.txt
```

## 라이선스

MIT License
