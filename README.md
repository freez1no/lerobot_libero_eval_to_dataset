# LeRobot LIBERO Evaluation Dataset Recorder & Viewer

LeRobot 라이브러리를 활용하여 LIBERO(Lifelong Robot Learning Benchmark) 시뮬레이션 환경에서 로봇 정책(VLA) 모델을 평가할 때, 평가 롤아웃 데이터를 표준 `LeRobotDataset` 규격으로 자동 녹화 및 저장하고, 그 결과를 웹 기반으로 직관적으로 분석할 수 있는 Streamlit 뷰어를 제공하는 확장 패키지입니다.

---

## 1. 개요 및 해결한 핵심 문제

### 배경 및 기존 한계점
기존 LeRobot의 `lerobot-eval` 파이프라인은 정책 모델 평가 시 롤아웃 비디오(MP4) 및 최종 성공/실패 여부를 담은 요약 메타데이터(`eval_info.json`)만을 출력합니다.
이로 인해 모델이 시뮬레이터와 상호작용하며 수집한 관측값(카메라 영상, 로봇 관절 상태), 행동(Action), 보상(Reward), 자연어 지시문(Task Instruction)을 포함하는 완전한 에피소드 데이터셋이 보존되지 않아, 평가 궤적을 후속 모델 재학습(Fine-tuning, DPO, RL 등)이나 오프라인 정책 분석에 재활용할 수 없는 한계가 있었습니다.

본 프로젝트에서는 이러한 한계를 극복하기 위해 `lerobot-eval`의 핵심 파이프라인을 수정하고, 실시간 모니터링 및 분석이 가능한 전용 대시보드를 구축하였습니다.

---

### 주요 문제 해결 및 기술적 구현 내용

#### 문제 1: 평가 롤아웃의 데이터셋 미생성 문제
- **원인 분석**: `lerobot-eval`의 기본 설정에서 `EvalConfig.recording`이 `False`로 비활성화되어 있었으며, 활성화하더라도 태스크별/환경별로 데이터셋이 파편화되거나 LIBERO 환경의 멀티태스크 구조를 온전히 반영하지 못했습니다.
- **해결 방식**: 
  - `src/lerobot/configs/default.py`의 `EvalConfig.recording` 기본값을 `True`로 전환하였습니다.
  - `eval_policy_all` 수준에서 단일 공유 `LeRobotDataset` 인스턴스를 초기화하여, 여러 벤치마크 스위트(Spatial, Object, Goal, 10)와 수십 개의 세부 태스크에 걸친 모든 롤아웃이 하나의 통일된 데이터셋 디렉토리(`dataset/`)로 순차 누적되도록 아키텍처를 개선하였습니다.
  - 평가 파이프라인 종료(`finally` 블록) 시 비동기 비디오 인코딩 대기 및 Parquet 메타데이터 푸터(`PAR1`)를 정상 마감하는 `finalize()`를 호출하여, 완전히 무결한 `LeRobotDataset v2.0/v3.0` 규격 데이터셋을 생성합니다.

#### 문제 2: 비디오 렌더링과 데이터셋 녹화의 상호 배제 문제
- **원인 분석**: 기존 구현에서는 `recording=True`일 경우 비디오 렌더링 경로(`videos_dir`)가 `None`으로 설정되어 비디오가 저장되지 않거나 디렉토리 간 충돌이 발생했습니다.
- **해결 방식**: 롤아웃 비디오 저장 경로(`Path(output_dir) / "videos"`)와 데이터셋 저장 경로(`Path(output_dir) / "dataset"`)를 상호 독립적인 파이프라인으로 분리하여, 롤아웃 비디오와 LeRobot 데이터셋이 동시에 누락 없이 저장되도록 개편하였습니다.

#### 문제 3: LIBERO 관측값 스키마 및 카메라 시점 불일치 문제
- **원인 분석**: 
  - LIBERO 시뮬레이터 카메라는 물리 엔진 시점 특성상 180도 회전되어 있어, 모델의 기대 시점 및 학습 데이터셋과 방향 불일치가 발생합니다.
  - 환경 원시 관측값(`raw_obs`)에서 8차원 로봇 상태(`observation.state`: 말단 위치 3 + 회전 3 + 그리퍼 2)가 적절히 추출되지 않고 유실되는 문제가 있었습니다.
- **해결 방식**: 
  - `_build_raw_frame`에서 LIBERO 카메라 이미지(`image`, `image2`)에 상하좌우 180도 반전(`[::-1, ::-1, :]`)을 적용하여 표준 시점으로 자동 교정하였습니다.
  - `rename_map`을 적용하여 모델 입력과 동일한 피처 이름(예: `observation.images.camera1`, `camera2`)으로 프레임 데이터를 매핑하였습니다.
  - `env_preprocessor`를 거친 정규화된 8차원 `observation.state`, 7차원 `action`, 보상/종료/성공 불리언 플래그, 자연어 `task` 텍스트를 완벽한 스키마로 추출하여 프레임 단위로 적재하였습니다.

#### 문제 4: 실시간 평가 모니터링 및 시각화 도구의 부재
- **원인 분석**: 수십~수백 개의 롤아웃을 수행하는 장시간 평가 과정에서 현재 진행 상황을 한눈에 파악하기 어렵고, Parquet 파일은 평가 완료 전까지 락이 걸려 공식 Rerun 도구로 즉시 확인하기 어렵습니다.
- **해결 방식**: Streamlit 기반의 통합 분석 뷰어(`eval_viewer`)를 개발하였습니다.
  - **스마트 경로 로더**: 텍스트 입력창 및 '경로 불러오기' 버튼을 제공하며, Windows/WSL/상대 경로 및 `dataset` 하위 폴더 입력을 자동으로 표준 경로로 정규화합니다.
  - **직관적 상단 KPI 대시보드**: 최상단에 `LIBERO Suites 수`, `Task 수`, `Episode 수`, `전체 성공 횟수 (예: 90 / 100)` 및 성공률 뱃지를 명확하게 표시합니다.
  - **실시간(In-Progress) 감지**: `eval_info.json`이 아직 작성되지 않은 실시간 평가 진행 중 상태에서도 지금까지 생성된 비디오와 데이터셋 메타정보를 자동으로 감지하여 브라우저에서 즉시 시청 및 분석할 수 있습니다.
  - **1:1 성공 vs 실패 비교 플레이어**: 성공 롤아웃과 실패 롤아웃을 나란히 배치하여 로봇 정책의 실패 원인(미끄러짐, 궤적 이탈 등)을 면밀히 분석할 수 있습니다.
  - **공식 도구 연동**: LeRobot 공식 CLI 뷰어(`lerobot-dataset-viz`) 명령어 원클릭 복사 및 Python 로딩 스크립트를 제공합니다.

---

## 2. 디렉토리 구조 및 파일 설명

이 저장소의 파일들을 기존 LeRobot 프로젝트 디렉토리에 그대로 복사하여 덮어씌우면 즉시 동일한 기능을 사용할 수 있습니다.

```
githubupload/
├── README.md                           # 프로젝트 설명서 (본 문서)
├── run_viewer.sh                       # Streamlit 뷰어 원클릭 실행 스크립트 (루트 바로가기)
├── src/
│   └── lerobot/
│       ├── configs/
│       │   └── default.py              # EvalConfig.recording=True 기본값 수정 설정 파일
│       └── scripts/
│           └── lerobot_eval.py         # LIBERO 데이터셋 변환, 비디오/데이터셋 동시 녹화 파이프라인
└── eval_viewer/
    ├── app.py                          # Streamlit 기반 LIBERO 평가 대시보드 웹 애플리케이션
    └── run_viewer.sh                   # eval_viewer 내부 실행 스크립트
```

### 각 파일의 상세 기능

1. `src/lerobot/configs/default.py`
   - `EvalConfig.recording`의 기본값을 `False`에서 `True`로 수정하여, 별도의 복잡한 옵션 없이도 기본 명령어로 데이터셋 녹화가 활성화되도록 지원합니다.

2. `src/lerobot/scripts/lerobot_eval.py`
   - `_env_features_to_dataset_features`: LIBERO 환경에 맞추어 카메라 2개, 8차원 상태, 7차원 액션, 보상, 성공 여부를 포함하는 표준 데이터셋 스키마를 구성합니다.
   - `_build_raw_frame`: 180도 회전 보정된 영상, 8차원 로봇 상태, 7차원 액션, 자연어 지시문을 프레임 단위 딕셔너리로 조립합니다.
   - `rollout`: 에피소드 단위 프레임 버퍼링 및 조기 종료/절단 에피소드의 데이터 누락 방지 플러시 로직을 처리합니다.
   - `eval_policy_all`: 전체 벤치마크 태스크를 포괄하는 단일 데이터셋 라이터를 유지하고, 종료 시 `dataset.finalize()`를 안전하게 호출합니다.

3. `eval_viewer/app.py`
   - 4개 주요 KPI 카드와 스위트별 진행률 카드를 포함하는 직관적인 메인 대시보드.
   - 3개 탭 구성:
     - 탭 1: 성과 요약 & 태스크 현황 (스위트별 막대 그래프, 태스크별 성공률 테이블, 검색 필터)
     - 탭 2: 롤아웃 비디오 (에피소드 선택 재생, 1:1 성공 vs 실패 비교 모드)
     - 탭 3: LeRobot 데이터셋 & 빠른 도구 (에피소드/프레임 수 요약, `lerobot-dataset-viz` 명령어 복사, Python 코드 예시)

4. `run_viewer.sh`
   - 환경에 설치된 Python 및 Streamlit 바이너리를 자동으로 감지하여 뷰어를 포트 8501로 구동하는 쉘 스크립트입니다.

---

## 3. 설치 및 적용 방법

### 1단계: 저장소 복사 (덮어씌우기)
기존에 설치된 `lerobot` 소스 코드 디렉토리로 이동하여, 본 저장소의 `src/` 폴더를 덮어씌웁니다.

```bash
# 본 저장소를 다운로드한 경로에서 기존 lerobot 경로로 복사
cp -r src/ <기존_lerobot_경로>/src/

# 뷰어 실행 디렉토리 복사
cp -r eval_viewer/ <원하는_작업_경로>/
cp run_viewer.sh <원하는_작업_경로>/
```

### 2단계: 뷰어 의존성 패키지 설치
평가 뷰어 실행을 위해 Streamlit과 Plotly를 환경에 설치합니다.

```bash
conda activate lerobot
pip install streamlit plotly
```

---

## 4. 평가 및 데이터셋 녹화 실행 방법

평가 실행 시 기존 명령어와 동일하게 실행하면, 별도의 추가 플래그 없이도 자동으로 `videos/` (롤아웃 영상)와 `dataset/` (LeRobot 표준 데이터셋)이 동시에 생성됩니다.

### 실행 명령어 예시
```bash
lerobot-eval \
  --policy.path="/mnt/c/wsl/dev/models/lerobot_libero" \
  --env.type=libero \
  --env.task=libero_spatial,libero_object,libero_goal,libero_10 \
  --eval.batch_size=1 \
  --eval.n_episodes=10 \
  --env.max_parallel_tasks=1 \
  --rename_map='{"observation.images.image": "observation.images.camera1", "observation.images.image2": "observation.images.camera2"}'
```

### 생성되는 결과 디렉토리 구조
평가 실행 결과 폴더(예: `outputs/eval/YYYY-MM-DD/HH-MM-SS/`) 내부에 다음과 같이 생성됩니다.

```
outputs/eval/YYYY-MM-DD/HH-MM-SS/
├── eval_info.json                      # 전체 및 태스크별 평가 통계 결과
├── videos/                             # 롤아웃 MP4 비디오
│   ├── libero_spatial_0/
│   │   ├── eval_episode_0.mp4
│   │   └── eval_episode_1.mp4
│   └── ...
└── dataset/                            # 표준 LeRobotDataset v2.0/v3.0
    ├── meta/
    │   ├── info.json                   # 데이터셋 메타데이터 (FPS, 총 프레임/에피소드)
    │   ├── tasks.parquet               # 자연어 태스크 목록
    │   └── episodes/                   # 에피소드 인덱스 매핑 파켓
    ├── data/                           # 센서 수치 데이터 파켓 (상태, 액션, 보상 등)
    └── videos/                         # 데이터셋 청크 비디오 (camera1, camera2)
```

---

## 5. Streamlit 평가 뷰어 사용 방법

### 뷰어 실행
WSL 또는 Linux 터미널에서 다음 명령어를 실행합니다.

```bash
./run_viewer.sh
```

실행 후 웹 브라우저를 열고 `http://localhost:8501`에 접속합니다.

### 주요 기능 가이드
1. **경로 불러오기**:
   - 사이드바의 입력창에 평가 폴더 경로(예: `outputs/eval/2026-10-23/09-22-58_libero_smolvla`)를 입력하고 **[경로 불러오기]** 버튼을 누릅니다.
   - 시스템에 존재하는 기존 실행들은 **[빠른 경로 선택]** 드롭다운에서 바로 선택할 수 있습니다.
2. **실시간 모니터링**:
   - 평가가 백그라운드에서 진행 중인 상태에서도 새로고침 버튼을 통해 현재까지 완료된 에피소드 비디오와 데이터셋 현황을 즉각 확인할 수 있습니다.
3. **롤아웃 비디오 탐색 및 비교**:
   - 원하는 태스크와 에피소드 번호를 선택하여 즉시 영상을 재생합니다.
   - `성공 vs 실패 1:1 비교` 옵션을 활성화하면 성공 궤적과 실패 궤적을 좌우에 나란히 놓고 재생할 수 있습니다.

---

## 6. 생성된 데이터셋 활용 방법

### 1) LeRobot 공식 CLI 뷰어 (`lerobot-dataset-viz`) 연동

#### 웹 브라우저 모드 (WSL 환경 권장)
```bash
lerobot-dataset-viz \
  --repo-id eval_dataset \
  --root outputs/eval/YYYY-MM-DD/HH-MM-SS/dataset \
  --episode-index 0 \
  --mode distant \
  --web-port 9090
```
명령어 실행 후 브라우저에서 `http://localhost:9090`에 접속하여 Rerun 기반 인터랙티브 타임라인으로 탐색합니다.

#### 데스크톱 창 모드 (WSLg GUI 환경)
```bash
lerobot-dataset-viz \
  --repo-id eval_dataset \
  --root outputs/eval/YYYY-MM-DD/HH-MM-SS/dataset \
  --episode-index 0
```

### 2) Python 스크립트에서 데이터셋 로드
```python
from lerobot.datasets import LeRobotDataset

# 저장된 평가 데이터셋 불러오기
dataset = LeRobotDataset("eval_dataset", root="outputs/eval/YYYY-MM-DD/HH-MM-SS/dataset")

print(f"총 에피소드: {dataset.num_episodes}")
print(f"총 프레임: {dataset.num_frames}")
print(f"피처 목록: {list(dataset.features.keys())}")

# 특정 에피소드의 첫 번째 프레임 확인
frame = dataset[0]
print("로봇 관절 상태 (8차원):", frame["observation.state"])
print("정책 액션 (7차원):", frame["action"])
print("자연어 지시문:", frame["task"])
print("성공 여부:", frame["next.success"])
```

### 3) Hugging Face Hub 업로드
표준 데이터셋 규격을 준수하므로 원클릭으로 Hub에 업로드하여 다른 연구자와 공유할 수 있습니다.

```python
dataset.push_to_hub("your-username/libero-eval-smolvla-dataset", private=True)
```
