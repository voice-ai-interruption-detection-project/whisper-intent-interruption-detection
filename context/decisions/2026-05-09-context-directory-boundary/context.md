# Context

## 선택지

1. `internal/`, `decisions/`, `archive/`, `temp/`를 루트에 계속 둔다.
2. 각 폴더를 `.claude/` 아래나 `docs/` 아래로 흡수한다.
3. 네 폴더를 `context/` 아래로 접고, 루트에는 실행/공개 축을 남긴다.

## 기각한 이유

루트에 계속 두면 개발이 진행될수록 `src/`, `data/`, `results/`, `docs/`와 운영 맥락 문서가 같은 무게로 보인다.

`.claude/` 아래로 넣으면 사람도 읽어야 하는 내부 기준과 결정 기록이 도구 전용 설정처럼 보인다.

`docs/` 아래로 넣으면 공개 문서와 내부 기준이 다시 섞인다.

## 판단이 바뀐 지점

`docs/`는 공개 문서라 루트에 둘 가치가 있지만, `internal/`, `decisions/`, `archive/`, `temp/`는 모두 작업 맥락층이라는 점이 분명해졌다.

따라서 `context/`를 내부 운영 맥락의 단일 진입점으로 두는 쪽이 개발자가 루트를 볼 때 덜 헷갈린다.

## 연결된 파일

- `context/README.md`
- `CLAUDE.md`
- `README.md`
- `.claude/rules/workflow.md`
- `.claude/agents/`
- `.codex/agents/`
- `.claude/skills/record-decision/SKILL.md`
