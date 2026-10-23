import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# LIBERO Task Knowledge Base (Standard 40 Tasks across 4 Suites)
# -----------------------------------------------------------------------------
LIBERO_TASKS_DB: Dict[str, Dict[int, Dict[str, str]]] = {
    "libero_spatial": {
        0: {
            "name": "pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate",
            "language": "pick up the black bowl between the plate and the ramekin and place it on the plate",
            "korean": "접시와 라메킨 사이의 검은 볼을 집어 접시 위에 놓기"
        },
        1: {
            "name": "pick_up_the_black_bowl_next_to_the_ramekin_and_place_it_on_the_plate",
            "language": "pick up the black bowl next to the ramekin and place it on the plate",
            "korean": "라메킨 옆의 검은 볼을 집어 접시 위에 놓기"
        },
        2: {
            "name": "pick_up_the_black_bowl_from_table_center_and_place_it_on_the_plate",
            "language": "pick up the black bowl from table center and place it on the plate",
            "korean": "테이블 중앙의 검은 볼을 집어 접시 위에 놓기"
        },
        3: {
            "name": "pick_up_the_black_bowl_on_the_cookie_box_and_place_it_on_the_plate",
            "language": "pick up the black bowl on the cookie box and place it on the plate",
            "korean": "쿠키 상자 위의 검은 볼을 집어 접시 위에 놓기"
        },
        4: {
            "name": "pick_up_the_black_bowl_in_the_top_drawer_of_the_wooden_cabinet_and_place_it_on_the_plate",
            "language": "pick up the black bowl in the top drawer of the wooden cabinet and place it on the plate",
            "korean": "원목 수납장 상단 서랍 안의 검은 볼을 집어 접시 위에 놓기"
        },
        5: {
            "name": "pick_up_the_black_bowl_on_the_ramekin_and_place_it_on_the_plate",
            "language": "pick up the black bowl on the ramekin and place it on the plate",
            "korean": "라메킨 위의 검은 볼을 집어 접시 위에 놓기"
        },
        6: {
            "name": "pick_up_the_black_bowl_next_to_the_cookie_box_and_place_it_on_the_plate",
            "language": "pick up the black bowl next to the cookie box and place it on the plate",
            "korean": "쿠키 상자 옆의 검은 볼을 집어 접시 위에 놓기"
        },
        7: {
            "name": "pick_up_the_black_bowl_on_the_stove_and_place_it_on_the_plate",
            "language": "pick up the black bowl on the stove and place it on the plate",
            "korean": "가스레인지 위의 검은 볼을 집어 접시 위에 놓기"
        },
        8: {
            "name": "pick_up_the_black_bowl_next_to_the_plate_and_place_it_on_the_plate",
            "language": "pick up the black bowl next to the plate and place it on the plate",
            "korean": "접시 옆의 검은 볼을 집어 접시 위에 놓기"
        },
        9: {
            "name": "pick_up_the_black_bowl_on_the_wooden_cabinet_and_place_it_on_the_plate",
            "language": "pick up the black bowl on the wooden cabinet and place it on the plate",
            "korean": "원목 수납장 위의 검은 볼을 집어 접시 위에 놓기"
        },
    },
    "libero_object": {
        0: {
            "name": "pick_up_the_alphabet_soup_and_place_it_in_the_basket",
            "language": "pick up the alphabet soup and place it in the basket",
            "korean": "알파벳 수프를 집어 바구니에 넣기"
        },
        1: {
            "name": "pick_up_the_cream_cheese_and_place_it_in_the_basket",
            "language": "pick up the cream cheese and place it in the basket",
            "korean": "크림치즈를 집어 바구니에 넣기"
        },
        2: {
            "name": "pick_up_the_salad_dressing_and_place_it_in_the_basket",
            "language": "pick up the salad dressing and place it in the basket",
            "korean": "샐러드 드레싱을 집어 바구니에 넣기"
        },
        3: {
            "name": "pick_up_the_bbq_sauce_and_place_it_in_the_basket",
            "language": "pick up the bbq sauce and place it in the basket",
            "korean": "바베큐 소스를 집어 바구니에 넣기"
        },
        4: {
            "name": "pick_up_the_ketchup_and_place_it_in_the_basket",
            "language": "pick up the ketchup and place it in the basket",
            "korean": "케첩을 집어 바구니에 넣기"
        },
        5: {
            "name": "pick_up_the_tomato_sauce_and_place_it_in_the_basket",
            "language": "pick up the tomato sauce and place it in the basket",
            "korean": "토마토 소스를 집어 바구니에 넣기"
        },
        6: {
            "name": "pick_up_the_butter_and_place_it_in_the_basket",
            "language": "pick up the butter and place it in the basket",
            "korean": "버터를 집어 바구니에 넣기"
        },
        7: {
            "name": "pick_up_the_milk_and_place_it_in_the_basket",
            "language": "pick up the milk and place it in the basket",
            "korean": "우유를 집어 바구니에 넣기"
        },
        8: {
            "name": "pick_up_the_chocolate_pudding_and_place_it_in_the_basket",
            "language": "pick up the chocolate pudding and place it in the basket",
            "korean": "초콜릿 푸딩을 집어 바구니에 넣기"
        },
        9: {
            "name": "pick_up_the_orange_juice_and_place_it_in_the_basket",
            "language": "pick up the orange juice and place it in the basket",
            "korean": "오렌지 주스를 집어 바구니에 넣기"
        },
    },
    "libero_goal": {
        0: {
            "name": "open_the_middle_drawer_of_the_cabinet",
            "language": "open the middle drawer of the cabinet",
            "korean": "수납장 가운데 서랍 열기"
        },
        1: {
            "name": "put_the_bowl_on_the_stove",
            "language": "put the bowl on the stove",
            "korean": "볼을 가스레인지 위에 올려놓기"
        },
        2: {
            "name": "put_the_wine_bottle_on_top_of_the_cabinet",
            "language": "put the wine bottle on top of the cabinet",
            "korean": "와인병을 수납장 위에 올려놓기"
        },
        3: {
            "name": "open_the_top_drawer_and_put_the_bowl_inside",
            "language": "open the top drawer and put the bowl inside",
            "korean": "상단 서랍을 열고 볼을 안에 넣기"
        },
        4: {
            "name": "put_the_bowl_on_top_of_the_cabinet",
            "language": "put the bowl on top of the cabinet",
            "korean": "볼을 수납장 위에 올려놓기"
        },
        5: {
            "name": "push_the_plate_to_the_front_of_the_stove",
            "language": "push the plate to the front of the stove",
            "korean": "접시를 가스레인지 앞으로 밀기"
        },
        6: {
            "name": "put_the_cream_cheese_in_the_bowl",
            "language": "put the cream cheese in the bowl",
            "korean": "크림치즈를 볼 안에 넣기"
        },
        7: {
            "name": "turn_on_the_stove",
            "language": "turn on the stove",
            "korean": "가스레인지 켜기"
        },
        8: {
            "name": "put_the_bowl_on_the_plate",
            "language": "put the bowl on the plate",
            "korean": "볼을 접시 위에 올려놓기"
        },
        9: {
            "name": "put_the_wine_bottle_on_the_rack",
            "language": "put the wine bottle on the rack",
            "korean": "와인병을 랙에 꽂아놓기"
        },
    },
    "libero_10": {
        0: {
            "name": "LIVING_ROOM_SCENE2_put_both_the_alphabet_soup_and_the_tomato_sauce_in_the_basket",
            "language": "put both the alphabet soup and the tomato sauce in the basket",
            "korean": "알파벳 수프와 토마토 소스를 둘 다 바구니에 넣기"
        },
        1: {
            "name": "LIVING_ROOM_SCENE2_put_both_the_cream_cheese_box_and_the_butter_in_the_basket",
            "language": "put both the cream cheese box and the butter in the basket",
            "korean": "크림치즈 상자와 버터를 둘 다 바구니에 넣기"
        },
        2: {
            "name": "KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it",
            "language": "turn on the stove and put the moka pot on it",
            "korean": "가스레인지를 켜고 모카포트를 올려놓기"
        },
        3: {
            "name": "KITCHEN_SCENE4_put_the_black_bowl_in_the_bottom_drawer_of_the_cabinet_and_close_it",
            "language": "put the black bowl in the bottom drawer of the cabinet and close it",
            "korean": "검은 볼을 수납장 하단 서랍에 넣고 서랍 닫기"
        },
        4: {
            "name": "LIVING_ROOM_SCENE5_put_the_white_mug_on_the_left_plate_and_put_the_yellow_and_white_mug_on_the_right_plate",
            "language": "put the white mug on the left plate and put the yellow and white mug on the right plate",
            "korean": "흰색 머그잔을 왼쪽 접시에, 노랑/흰색 머그잔을 오른쪽 접시에 놓기"
        },
        5: {
            "name": "STUDY_SCENE1_pick_up_the_book_and_place_it_in_the_back_compartment_of_the_caddy",
            "language": "pick up the book and place it in the back compartment of the caddy",
            "korean": "책을 집어 캐디 뒤쪽 수납칸에 넣기"
        },
        6: {
            "name": "LIVING_ROOM_SCENE6_put_the_white_mug_on_the_plate_and_put_the_chocolate_pudding_to_the_right_of_the_plate",
            "language": "put the white mug on the plate and put the chocolate pudding to the right of the plate",
            "korean": "흰색 머그잔을 접시 위에 올리고, 초콜릿 푸딩을 접시 오른쪽에 놓기"
        },
        7: {
            "name": "LIVING_ROOM_SCENE1_put_both_the_alphabet_soup_and_the_cream_cheese_box_in_the_basket",
            "language": "put both the alphabet soup and the cream cheese box in the basket",
            "korean": "알파벳 수프와 크림치즈 상자를 둘 다 바구니에 넣기"
        },
        8: {
            "name": "KITCHEN_SCENE8_put_both_moka_pots_on_the_stove",
            "language": "put both moka pots on the stove",
            "korean": "모카포트 2개를 모두 가스레인지 위에 올려놓기"
        },
        9: {
            "name": "KITCHEN_SCENE6_put_the_yellow_and_white_mug_in_the_microwave_and_close_it",
            "language": "put the yellow and white mug in the microwave and close it",
            "korean": "노랑/흰색 머그잔을 전자레인지에 넣고 문 닫기"
        },
    }
}

def get_task_info(task_group: str, task_id: int) -> Dict[str, str]:
    """Retrieve human-readable task information with fallback."""
    if task_group in LIBERO_TASKS_DB and task_id in LIBERO_TASKS_DB[task_group]:
        return LIBERO_TASKS_DB[task_group][task_id]
    
    return {
        "name": f"{task_group}_{task_id}",
        "language": f"Task {task_id} of {task_group}",
        "korean": f"{task_group} 태스크 {task_id}"
    }

# -----------------------------------------------------------------------------
# Path Resolution & Discovery
# -----------------------------------------------------------------------------
SEARCH_ROOTS = [
    Path("/home/freezino-inc/outputs/eval"),
    Path("/home/freezino-inc/lerobot/outputs/eval"),
    Path("./outputs/eval"),
    Path("./lerobot/outputs/eval"),
    Path("/mnt/c/wsl/dev/models/lerobot_libero/outputs/eval"),
]

def normalize_eval_path(p_str: str) -> Optional[Path]:
    """Robustly parse Windows, WSL, relative, and dataset paths to the eval run root."""
    if not p_str or not p_str.strip():
        return None
    
    raw = p_str.strip().replace("\\", "/")
    
    # Handle user-friendly shortcuts
    if raw.startswith("freezino-inc/"):
        raw = "/home/" + raw
    elif raw.startswith("~/"):
        raw = os.path.expanduser(raw)
    elif len(raw) >= 2 and raw[1] == ":":
        drive = raw[0].lower()
        raw = f"/mnt/{drive}" + raw[2:]
        
    p = Path(raw)
    
    # Try resolving relative to common bases
    if not p.exists():
        candidates = [
            Path("/home/freezino-inc") / raw,
            Path("/home/freezino-inc/lerobot") / raw,
            Path.cwd() / raw
        ]
        for c in candidates:
            if c.exists():
                p = c
                break
                
    if not p.exists():
        return None
        
    # If pointed to 'dataset' or 'videos', redirect to parent run directory
    if p.name in ("dataset", "videos") and (p.parent / "videos").exists() or (p.parent / "eval_info.json").exists():
        return p.parent.resolve()
        
    return p.resolve()

def find_eval_runs(custom_dir: Optional[str] = None) -> List[Path]:
    """Discover all eval runs (both completed and in-progress)."""
    candidates = []
    roots = list(SEARCH_ROOTS)
    if custom_dir:
        norm_custom = normalize_eval_path(custom_dir)
        if norm_custom and norm_custom.is_dir():
            candidates.append(norm_custom)

    for root in roots:
        if not root.exists():
            continue
        try:
            for p in root.rglob("*"):
                if p.is_dir() and p.name not in ("dataset", "videos", "data", "meta", "images"):
                    if (p / "eval_info.json").exists() or (p / "videos").exists() or (p / "dataset").exists():
                        candidates.append(p.resolve())
        except Exception:
            continue
    
    # Deduplicate & sort newest first
    unique_runs = []
    seen = set()
    for run in sorted(candidates, key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True):
        s_path = str(run)
        if s_path not in seen:
            seen.add(s_path)
            unique_runs.append(run)
    return unique_runs

def resolve_video_path(raw_path: str, run_dir: Path) -> Optional[Path]:
    """Resolve episode video path on disk."""
    if not raw_path:
        return None
    p = Path(raw_path)
    if p.is_file():
        return p
    
    if (run_dir / raw_path).is_file():
        return run_dir / raw_path
    
    # Search under run_dir/videos
    parts = p.parts
    if "videos" in parts:
        v_idx = parts.index("videos")
        rel = Path(*parts[v_idx:])
        cand = run_dir / rel
        if cand.is_file():
            return cand
    
    cand = run_dir / "videos" / p.name
    if cand.is_file():
        return cand
        
    return None

# -----------------------------------------------------------------------------
# Data Loader (Handles both completed runs and in-progress runs)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=5)
def load_eval_data(run_dir_str: str) -> Tuple[Dict[str, Any], Dict[str, Any], pd.DataFrame, bool, Dict[str, Any]]:
    """Loads eval data from eval_info.json or dynamically from videos/dataset directory."""
    run_dir = Path(run_dir_str)
    eval_json = run_dir / "eval_info.json"
    dataset_dir = run_dir / "dataset"
    videos_dir = run_dir / "videos"
    
    is_in_progress = not eval_json.exists()
    
    # Case 1: Completed run with eval_info.json
    if eval_json.exists():
        with open(eval_json, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        overall = raw_data.get("overall", {})
        per_group = raw_data.get("per_group", {})
        per_task = raw_data.get("per_task", [])
        
        task_rows = []
        for item in per_task:
            group = item.get("task_group", "")
            tid = item.get("task_id", 0)
            n_ep = item.get("n_episodes", 0)
            n_succ = item.get("n_success", 0)
            pc_succ = item.get("pc_success", 0.0)
            ci95 = item.get("pc_success_ci95", [pc_succ, pc_succ])
            
            metrics = item.get("metrics", {})
            successes = metrics.get("successes", [])
            sum_rewards = metrics.get("sum_rewards", [])
            video_paths = metrics.get("video_paths", [])
            
            info = get_task_info(group, tid)
            
            task_rows.append({
                "group": group,
                "task_id": tid,
                "task_key": f"{group}_{tid}",
                "task_name": info["name"],
                "language": info["language"],
                "korean": info.get("korean", info["language"]),
                "n_episodes": n_ep,
                "n_success": n_succ,
                "pc_success": pc_succ,
                "ci95_low": ci95[0] if len(ci95) > 0 else pc_succ,
                "ci95_high": ci95[1] if len(ci95) > 1 else pc_succ,
                "avg_reward": sum(sum_rewards)/len(sum_rewards) if sum_rewards else 0.0,
                "successes": successes,
                "sum_rewards": sum_rewards,
                "video_paths": video_paths
            })
            
        df_tasks = pd.DataFrame(task_rows)
        return overall, per_group, df_tasks, is_in_progress, raw_data

    # Case 2: In-progress run (parse videos and dataset meta directly)
    task_rows = []
    per_group = {}
    total_episodes_found = 0
    raw_data = {"status": "in_progress"}
    
    if videos_dir.exists():
        task_folders = sorted(
            [d for d in videos_dir.iterdir() if d.is_dir()],
            key=lambda d: d.name
        )
        for tf in task_folders:
            folder_name = tf.name # e.g. libero_spatial_0
            parts = folder_name.rsplit("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                group = parts[0]
                tid = int(parts[1])
            else:
                group = folder_name
                tid = 0
                
            v_files = sorted(
                list(tf.glob("eval_episode_*.mp4")),
                key=lambda p: int(p.stem.split("_")[-1]) if p.stem.split("_")[-1].isdigit() else 0
            )
            n_ep = len(v_files)
            total_episodes_found += n_ep
            info = get_task_info(group, tid)
            
            task_rows.append({
                "group": group,
                "task_id": tid,
                "task_key": f"{group}_{tid}",
                "task_name": info["name"],
                "language": info["language"],
                "korean": info.get("korean", info["language"]),
                "n_episodes": n_ep,
                "n_success": 0,
                "pc_success": 0.0,
                "ci95_low": 0.0,
                "ci95_high": 0.0,
                "avg_reward": 0.0,
                "successes": [True] * n_ep, # Allow watching all in-progress
                "sum_rewards": [0.0] * n_ep,
                "video_paths": [str(v) for v in v_files]
            })
            
            if group not in per_group:
                per_group[group] = {
                    "n_episodes": 0,
                    "n_success": 0,
                    "pc_success": 0.0,
                    "avg_sum_reward": 0.0,
                    "pc_success_ci95": [0.0, 0.0]
                }
            per_group[group]["n_episodes"] += n_ep

    # Check dataset meta info if available
    ds_info_file = dataset_dir / "meta" / "info.json"
    if ds_info_file.exists():
        try:
            with open(ds_info_file, "r", encoding="utf-8") as f:
                ds_meta = json.load(f)
            raw_data["dataset_info"] = ds_meta
            if ds_meta.get("total_episodes", 0) > total_episodes_found:
                total_episodes_found = ds_meta.get("total_episodes")
        except Exception:
            pass

    df_tasks = pd.DataFrame(task_rows)
    overall = {
        "n_episodes": total_episodes_found,
        "n_success": 0,
        "pc_success": 0.0,
        "pc_success_ci95": [0.0, 0.0],
        "eval_s": 0
    }
    return overall, per_group, df_tasks, is_in_progress, raw_data

# -----------------------------------------------------------------------------
# Streamlit App Setup & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LeRobot LIBERO Eval Viewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-card-title {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card-value {
        font-size: 2.1rem;
        font-weight: 800;
        margin-top: 4px;
        color: #38bdf8;
    }
    .metric-card-sub {
        font-size: 0.84rem;
        color: #cbd5e1;
        margin-top: 3px;
    }
    
    /* Prominent Success Badge */
    .badge-success-large {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 8px;
        border: 1px solid rgba(16, 185, 129, 0.4);
        display: inline-block;
        margin-left: 8px;
    }
    
    /* Suite Summary Cards */
    .suite-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .suite-card-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    .suite-card-rate {
        font-size: 1.35rem;
        font-weight: 800;
        color: #10b981;
    }
    
    /* Pills & Badges */
    .badge-success {
        background-color: rgba(34, 197, 94, 0.18);
        color: #16a34a;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(34, 197, 94, 0.3);
        display: inline-block;
        font-size: 0.85rem;
    }
    .badge-failure {
        background-color: rgba(239, 68, 68, 0.18);
        color: #dc2626;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        display: inline-block;
        font-size: 0.85rem;
    }
    .badge-pill-success {
        background-color: #22c55e;
        color: white;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 4px;
        display: inline-block;
    }
    .badge-pill-failure {
        background-color: #ef4444;
        color: white;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 4px;
        display: inline-block;
    }
    .task-container {
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 14px 18px;
        margin-bottom: 12px;
        background-color: rgba(255, 255, 255, 0.02);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar: Path Selector, Loader Button & Controls (Requirement 1)
# -----------------------------------------------------------------------------
st.sidebar.title("🤖 LIBERO Eval Viewer")
st.sidebar.caption("LeRobot Evaluation Results & Rollout Visualizer")

# Scan available runs
available_runs = find_eval_runs()

# Initialize session state for current directory
if "current_run_path" not in st.session_state:
    if available_runs:
        st.session_state["current_run_path"] = str(available_runs[0])
    else:
        st.session_state["current_run_path"] = "/home/freezino-inc/outputs/eval"

st.sidebar.markdown("### 📂 평가 데이터 경로 설정")
st.sidebar.caption("결과 폴더(또는 `dataset`, `videos` 폴더) 경로를 직접 입력하고 불러올 수 있습니다.")

# Manual path input
input_path_val = st.sidebar.text_input(
    "디렉토리 경로 입력",
    value=st.session_state["current_run_path"],
    placeholder="/path/to/outputs/eval/YYYY-MM-DD/HH-MM-SS",
    help="WSL 경로, 윈도우 경로, 상대 경로 모두 지원됩니다."
)

btn_c1, btn_c2 = st.sidebar.columns([2, 1])
with btn_c1:
    load_clicked = st.button("📂 경로 불러오기", type="primary", use_container_width=True)
with btn_c2:
    refresh_clicked = st.button("🔄 새로고침", use_container_width=True)

if load_clicked:
    resolved_cand = normalize_eval_path(input_path_val)
    if resolved_cand and resolved_cand.exists():
        st.session_state["current_run_path"] = str(resolved_cand)
        st.cache_data.clear()
        st.toast(f"✅ 경로를 성공적으로 불러왔습니다: {resolved_cand.name}")
        st.rerun()
    else:
        st.sidebar.error("❌ 입력한 경로를 찾을 수 없습니다. 경로를 확인해주세요.")

if refresh_clicked:
    st.cache_data.clear()
    st.rerun()

# Quick Selection Dropdown
if available_runs:
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### ⚡ 빠른 경로 선택 (자동 감지된 실행 목록)")
    
    def format_run_label(p: Path) -> str:
        date_folder = p.parent.name
        run_name = p.name
        status_tag = "✅ 완료" if (p / "eval_info.json").exists() else "🟢 진행중"
        return f"{status_tag} {date_folder} / {run_name}"

    run_opts = [str(r) for r in available_runs]
    curr_idx = run_opts.index(st.session_state["current_run_path"]) if st.session_state["current_run_path"] in run_opts else 0

    selected_quick = st.sidebar.selectbox(
        "목록에서 선택",
        options=run_opts,
        index=curr_idx,
        format_func=lambda x: format_run_label(Path(x)),
        label_visibility="collapsed"
    )
    if selected_quick != st.session_state["current_run_path"]:
        st.session_state["current_run_path"] = selected_quick
        st.cache_data.clear()
        st.rerun()

current_run_dir = Path(st.session_state["current_run_path"])
st.sidebar.markdown(f"**현재 경로:**  \n`{current_run_dir}`")

# -----------------------------------------------------------------------------
# Data Loading & Validation
# -----------------------------------------------------------------------------
if not current_run_dir.exists():
    st.error(f"⚠️ 선택된 경로가 존재하지 않습니다: `{current_run_dir}`")
    st.info("사이드바에서 올바른 평가 결과 경로를 입력하고 **[📂 경로 불러오기]** 버튼을 눌러주세요.")
    st.stop()

overall, per_group, df_tasks, is_in_progress, raw_data = load_eval_data(str(current_run_dir))

# -----------------------------------------------------------------------------
# Top Header & Major KPI Dashboard (Requirement 2)
# -----------------------------------------------------------------------------
st.title("🤖 LeRobot LIBERO Evaluation Viewer")

if is_in_progress:
    st.info(f"⏳ **평가 녹화가 실시간 진행 중입니다!**  \n현재까지 저장된 비디오 및 데이터셋을 실시간으로 탐색할 수 있습니다. 평가가 완료되면 정밀 성공률 지표가 자동으로 갱신됩니다.")
else:
    st.caption(f"📂 분석 대상: `{current_run_dir.name}` ({current_run_dir.parent.name})")

# Calculate Top KPIs
# 1. LIBERO Suites Count
n_suites = len(per_group) if per_group else (df_tasks["group"].nunique() if not df_tasks.empty else 0)
suite_names_str = ", ".join(list(per_group.keys())) if per_group else ("LIBERO Suites" if n_suites > 0 else "None")

# 2. Task Count
n_tasks = len(df_tasks)

# 3. Episode Count
total_eps = overall.get("n_episodes", int(df_tasks["n_episodes"].sum()) if not df_tasks.empty else 0)

# 4. Overall Success Count ("90 / 100")
total_succ = overall.get("n_success", int(df_tasks["n_success"].sum()) if not df_tasks.empty else 0)
overall_pc = overall.get("pc_success", (total_succ / total_eps * 100.0) if total_eps > 0 else 0.0)

# Render 4 Top KPI Cards
kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)

with kpi_c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">📁 LIBERO Suites</div>
        <div class="metric-card-value" style="color: #a78bfa;">{n_suites} Suites</div>
        <div class="metric-card-sub">{suite_names_str}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">📋 Task 수</div>
        <div class="metric-card-value" style="color: #38bdf8;">{n_tasks} Tasks</div>
        <div class="metric-card-sub">평가 대상 태스크 총합</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">🎬 Episode 수</div>
        <div class="metric-card-value" style="color: #fbbf24;">{total_eps} Episodes</div>
        <div class="metric-card-sub">총 롤아웃 수행 횟수</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c4:
    success_color = "#34d399" if overall_pc >= 70 else ("#f59e0b" if overall_pc >= 40 else "#f87171")
    if is_in_progress:
        succ_display = f"{total_eps}개 녹화중"
        sub_text = "진행 중 (실시간 집계)"
    else:
        succ_display = f"{total_succ} / {total_eps}"
        sub_text = f"성공률: {overall_pc:.1f}%"
        
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">🎯 전체 성공 횟수 (Success)</div>
        <div style="display: flex; align-items: baseline;">
            <span class="metric-card-value" style="color: {success_color};">{succ_display}</span>
            <span class="badge-success-large" style="color: {success_color};">{overall_pc:.1f}%</span>
        </div>
        <div class="metric-card-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)

# Suite-by-Suite Mini Summary Row
if per_group:
    s_cols = st.columns(len(per_group))
    for i, (g_name, g_info) in enumerate(per_group.items()):
        g_eps = g_info.get("n_episodes", 0)
        g_succ = g_info.get("n_success", 0)
        g_rate = g_info.get("pc_success", (g_succ / g_eps * 100) if g_eps > 0 else 0.0)
        with s_cols[i]:
            st.markdown(f"""
            <div class="suite-card">
                <div class="suite-card-name">🔹 {g_name}</div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 4px;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">{g_succ} / {g_eps}</span>
                    <span class="suite-card-rate">{g_rate:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(1.0, max(0.0, g_rate / 100.0)))

st.write("")

# -----------------------------------------------------------------------------
# Main Simplified 3-Tab Interface (Requirement 3)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 성과 요약 & 태스크 현황 (Overview & Tasks)",
    "🎬 롤아웃 비디오 (Rollout Videos)",
    "📦 LeRobot 데이터셋 & 빠른 도구 (Dataset & Tools)"
])

# -----------------------------------------------------------------------------
# TAB 1: 성과 요약 & 태스크 목록
# -----------------------------------------------------------------------------
with tab1:
    col_chart, col_stat = st.columns([3, 2])
    
    with col_chart:
        if per_group:
            fig_suite = go.Figure()
            colors = ["#38bdf8", "#34d399", "#fbbf24", "#a78bfa"]
            s_names = list(per_group.keys())
            s_rates = [per_group[k].get("pc_success", 0.0) for k in s_names]
            
            fig_suite.add_trace(go.Bar(
                x=s_names,
                y=s_rates,
                text=[f"{v:.1f}%" for v in s_rates],
                textposition="auto",
                marker=dict(color=colors[:len(s_names)]),
                hovertemplate="<b>%{x}</b><br>성공률: %{y:.1f}%<extra></extra>"
            ))
            fig_suite.update_layout(
                title="LIBERO Suite별 성공률 현황",
                yaxis=dict(title="Success Rate (%)", range=[0, 105]),
                xaxis=dict(title=""),
                height=320,
                margin=dict(l=30, r=20, t=40, b=30),
                template="plotly_dark"
            )
            st.plotly_chart(fig_suite, use_container_width=True)
        else:
            st.info("스위트별 통계 집계 중입니다.")

    with col_stat:
        st.markdown("##### 📌 평가 실행 요약")
        eval_s = overall.get("eval_s", 0)
        mins = int(eval_s // 60)
        secs = int(eval_s % 60)
        time_text = f"{mins}분 {secs}초" if mins > 0 else f"{secs}초"
        
        stat_rows = [
            {"항목": "상태", "값": "🟢 실시간 녹화 중" if is_in_progress else "✅ 평가 완료"},
            {"항목": "전체 성공률", "값": f"{overall_pc:.1f}% ({total_succ} / {total_eps})" if not is_in_progress else f"{total_eps} 에피소드 녹화됨"},
            {"항목": "평가 태스크 수", "값": f"{n_tasks}개 태스크"},
            {"항목": "소요 시간", "값": time_text if eval_s > 0 else "측정 중"}
        ]
        st.dataframe(pd.DataFrame(stat_rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📋 태스크 목록 및 에피소드 성공 현황")

    # Filters
    f1, f2, f3 = st.columns([1.5, 1.5, 3])
    with f1:
        s_options = ["전체 (All)"] + sorted(df_tasks["group"].unique().tolist()) if not df_tasks.empty else ["전체"]
        sel_s = st.selectbox("스위트 필터", s_options)
    with f2:
        status_opts = ["전체", "성공률 높은 순", "성공률 낮은 순"]
        sel_sort = st.selectbox("정렬 기준", status_opts)
    with f3:
        search_q = st.text_input("🔍 태스크 지시문 검색 (한글 또는 영문)", placeholder="예: bowl, stove, 서랍, 접시...")

    # Filter DataFrame
    df_show = df_tasks.copy()
    if not df_show.empty:
        if sel_s != "전체 (All)":
            df_show = df_show[df_show["group"] == sel_s]
        if search_q.strip():
            sq = search_q.strip().lower()
            df_show = df_show[
                df_show["language"].str.lower().str.contains(sq) |
                df_show["korean"].str.lower().str.contains(sq) |
                df_show["task_name"].str.lower().str.contains(sq)
            ]
        if sel_sort == "성공률 높은 순":
            df_show = df_show.sort_values(by="pc_success", ascending=False)
        elif sel_sort == "성공률 낮은 순":
            df_show = df_show.sort_values(by="pc_success", ascending=True)

        for _, row in df_show.iterrows():
            succ_rate = row["pc_success"]
            badge_cls = "badge-success" if succ_rate >= 60 else "badge-failure"
            
            with st.container():
                st.markdown(f"""
                <div class="task-container">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #94a3b8; font-weight: 600; font-size: 0.82rem;">[{row['group'].upper()}] Task #{row['task_id']}</span>
                            <h4 style="margin: 2px 0 4px 0; color: #f8fafc;">"{row['language']}"</h4>
                            <div style="color: #cbd5e1; font-size: 0.88rem;">🇰🇷 {row['korean']}</div>
                        </div>
                        <div style="text-align: right; min-width: 140px;">
                            <span class="{badge_cls}">{row['n_success']} / {row['n_episodes']} ({succ_rate:.0f}%)</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_pills, c_btn = st.columns([5, 1])
                with c_pills:
                    pill_html = ""
                    for ep_idx, succ in enumerate(row["successes"]):
                        if succ:
                            pill_html += f"<span class='badge-pill-success'>Ep {ep_idx} 🟢</span> "
                        else:
                            pill_html += f"<span class='badge-pill-failure'>Ep {ep_idx} 🔴</span> "
                    st.markdown(pill_html, unsafe_allow_html=True)
                with c_btn:
                    if st.button("🎬 영상 보기", key=f"btn_nav_{row['task_key']}"):
                        st.session_state["selected_task_key"] = row["task_key"]
                        st.toast(f"'{row['language'][:30]}...' 선택됨! '롤아웃 비디오' 탭을 확인하세요.")

# -----------------------------------------------------------------------------
# TAB 2: 롤아웃 비디오 (Rollout Videos)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("🎬 에피소드 롤아웃 비디오 플레이어")

    if df_tasks.empty:
        st.warning("녹화된 비디오가 감지되지 않았습니다.")
    else:
        # Task Selection
        task_keys = df_tasks["task_key"].tolist()
        def_idx = 0
        if "selected_task_key" in st.session_state and st.session_state["selected_task_key"] in task_keys:
            def_idx = task_keys.index(st.session_state["selected_task_key"])

        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            sel_task_key = st.selectbox(
                "태스크 선택",
                options=task_keys,
                index=def_idx,
                format_func=lambda k: f"[{df_tasks.loc[df_tasks['task_key']==k, 'group'].values[0]}_{df_tasks.loc[df_tasks['task_key']==k, 'task_id'].values[0]}] {df_tasks.loc[df_tasks['task_key']==k, 'language'].values[0]}"
            )
        
        task_row = df_tasks[df_tasks["task_key"] == sel_task_key].iloc[0]
        
        with t_col2:
            st.markdown(f"**성공 횟수:**  \n### {task_row['n_success']} / {task_row['n_episodes']} ({task_row['pc_success']:.0f}%)")

        st.markdown(f"**지시문 (Instruction):** *\"{task_row['language']}\"* ({task_row['korean']})")

        successes = task_row["successes"]
        v_paths = task_row["video_paths"]
        sum_rewards = task_row["sum_rewards"]

        # View Mode Toggle
        c_mode, c_filter = st.columns([1, 2])
        with c_mode:
            compare_mode = st.checkbox("🔄 성공 vs 실패 나란히 1:1 비교 모드", value=False)
        with c_filter:
            filter_ep = st.radio("에피소드 필터", ["전체 에피소드", "성공만 (🟢)", "실패만 (🔴)"], horizontal=True)

        if not compare_mode:
            # Single Video View
            candidate_eps = list(range(len(v_paths)))
            if filter_ep == "성공만 (🟢)" and any(successes):
                candidate_eps = [i for i in candidate_eps if i < len(successes) and successes[i]]
            elif filter_ep == "실패만 (🔴)" and not all(successes):
                candidate_eps = [i for i in candidate_eps if i < len(successes) and not successes[i]]

            if not candidate_eps:
                st.warning("선택한 필터 조건에 해당하는 에피소드가 없습니다.")
            else:
                sel_ep = st.selectbox(
                    "재생할 에피소드 번호 선택",
                    options=candidate_eps,
                    format_func=lambda i: f"Episode #{i} {'(🟢 성공)' if (i < len(successes) and successes[i]) else '(🔴 실패)'}"
                )

                raw_v = v_paths[sel_ep] if sel_ep < len(v_paths) else None
                resolved_v = resolve_video_path(raw_v, current_run_dir)
                
                is_succ = successes[sel_ep] if sel_ep < len(successes) else False
                st.markdown(f"#### Episode #{sel_ep} {'<span class=\"badge-success\">🟢 성공</span>' if is_succ else '<span class=\"badge-failure\">🔴 실패</span>'}", unsafe_allow_html=True)

                if resolved_v and resolved_v.is_file():
                    st.video(str(resolved_v))
                    st.caption(f"📁 비디오 파일: `{resolved_v}`")
                else:
                    st.error(f"비디오 파일을 불러올 수 없습니다: {raw_v}")

        else:
            # Side-by-Side Comparison
            succ_idx = [i for i, s in enumerate(successes) if s]
            fail_idx = [i for i, s in enumerate(successes) if not s]

            if not succ_idx or not fail_idx:
                st.info("비교할 성공/실패 에피소드가 양쪽 모두 존재하지 않습니다.")
            else:
                cmp1, cmp2 = st.columns(2)
                with cmp1:
                    st.markdown("#### 🟢 성공 에피소드")
                    s_ep = st.selectbox("성공 에피소드", succ_idx, format_func=lambda x: f"Ep #{x}")
                    s_path = resolve_video_path(v_paths[s_ep], current_run_dir)
                    if s_path and s_path.is_file():
                        st.video(str(s_path))
                with cmp2:
                    st.markdown("#### 🔴 실패 에피소드")
                    f_ep = st.selectbox("실패 에피소드", fail_idx, format_func=lambda x: f"Ep #{x}")
                    f_path = resolve_video_path(v_paths[f_ep], current_run_dir)
                    if f_path and f_path.is_file():
                        st.video(str(f_path))

# -----------------------------------------------------------------------------
# TAB 3: LeRobot 데이터셋 & 빠른 도구 (Dataset & Tools)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📦 LeRobot 데이터셋 상태 및 공식 뷰어 연동")

    ds_dir = current_run_dir / "dataset"
    if ds_dir.exists():
        st.success(f"💾 **LeRobot 표준 데이터셋 폴더 감지됨:** `{ds_dir}`")
        
        # Meta Info
        meta_info_file = ds_dir / "meta" / "info.json"
        if meta_info_file.exists():
            try:
                with open(meta_info_file, "r", encoding="utf-8") as f:
                    meta_dict = json.load(f)
                
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                with m_c1:
                    st.metric("총 에피소드", f"{meta_dict.get('total_episodes', 0):,} 개")
                with m_c2:
                    st.metric("총 프레임 수", f"{meta_dict.get('total_frames', 0):,} frames")
                with m_c3:
                    st.metric("FPS", f"{meta_dict.get('fps', 20)} fps")
                with m_c4:
                    st.metric("포맷 버전", meta_dict.get("codebase_version", "v3.0"))

                features_list = list(meta_dict.get("features", {}).keys())
                st.markdown(f"**저장된 센서 및 피처 (`features`):** `{', '.join(features_list)}`")
            except Exception as e:
                st.caption(f"메타데이터 파싱 오류: {e}")

        st.markdown("---")
        st.markdown("### 🖥️ LeRobot 공식 데이터셋 뷰어 (`lerobot-dataset-viz`) 실행 명령어")
        st.markdown("아래 명령어를 WSL 터미널에 복사하여 붙여넣으면, Rerun 기반의 타임라인 인터랙티브 뷰어로 데이터셋을 확인하실 수 있습니다.")

        cmd_web = f"""lerobot-dataset-viz \\
  --repo-id eval_dataset \\
  --root {ds_dir} \\
  --episode-index 0 \\
  --mode distant \\
  --web-port 9090"""
        
        st.markdown("**1) 웹 브라우저 모드 (WSL 환경 추천 🌐)** - 실행 후 `http://localhost:9090` 접속:")
        st.code(cmd_web, language="bash")

        cmd_gui = f"""lerobot-dataset-viz \\
  --repo-id eval_dataset \\
  --root {ds_dir} \\
  --episode-index 0"""
        
        st.markdown("**2) 데스크톱 창 모드 (WSLg GUI):**")
        st.code(cmd_gui, language="bash")

        st.markdown("---")
        st.markdown("### 🐍 Python 데이터셋 로드 코드 예시")
        py_code = f"""from lerobot.datasets import LeRobotDataset

# 평가 완료된 데이터셋 로드
dataset = LeRobotDataset("eval_dataset", root="{ds_dir}")

print(f"총 에피소드: {{dataset.num_episodes}}")
print(f"총 프레임: {{dataset.num_frames}}")

# 첫 번째 프레임 확인
frame = dataset[0]
print("Action:", frame["action"])
print("State:", frame["observation.state"])
print("Task:", frame["task"])
"""
        st.code(py_code, language="python")
    else:
        st.info("선택된 디렉토리에 `dataset/` 폴더가 아직 생성되지 않았습니다.")
