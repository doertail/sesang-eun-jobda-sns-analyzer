# 시스템 설계

[[1. Plan]] | [[3. Log]] | [[4. Idea]] | [[5. Reference]] | [[6. Retrospective]] | [[0. ReadMe]]

## 데이터 흐름
1. 사용자 입력 → 2. 데이터 수집 → 3. 분석 → 4. 결과 출력

## 주요 알고리즘
- 공통 팔로우 분석
- bio 키워드 매칭

## 화면 설계(와이어프레임)
- (여기에 간단한 화면 구상이나 와이어프레임을 추가하세요) 

## ⚙️ 연결 강도 추론 기능 기술 설계

`1. Plan.md`의 고도화 계획에 따라, 연결 강도 추론 기능을 위한 구체적인 기술 설계를 정의한다.

### 1. 데이터 구조 정의

네트워크를 구성하는 노드(인물)와 엣지(관계)의 데이터 구조를 다음과 같이 확장한다.

**Node (Person) Object:**
```json
{
  "id": "user_id",
  "name": "사용자 이름",
  "communities": ["community_id_1", "community_id_2"] // 소속 커뮤니티 (예: '서울대학교', '삼성전자')
  // ... 기타 정보
}
```

**Edge (Connection) Object:**
```json
{
  "source": "user_id_A",
  "target": "user_id_B",
  "strength": "weak", // 'strong' 또는 'weak', 추론 전 기본값
  "is_inferred": false // 강도가 추론되었는지 여부
}
```

### 2. 핵심 모듈 및 함수 설계

#### `TieStrengthInference` 모듈
- **`infer_strength(graph, communities)`**: 메인 함수. 전체 그래프와 커뮤니티 정보를 받아 각 엣지의 `strength`를 결정하고 업데이트한다.
  - **Input**: `graph` (Node 및 Edge 객체들의 집합), `communities` (커뮤니티 ID와 멤버 목록)
  - **Output**: `strength` 속성이 업데이트된 `graph` 객체
  - **Logic (논문 기반의 유사 코드)**:
    1. 모든 엣지를 'strong' 후보로 초기 설정한다.
    2. 각 'strong' 엣지에 대해 STC(강한 삼각관계 닫힘) 위반 수를 계산한다.
    3. STC 위반을 가장 많이 일으키는 엣지부터 'weak'으로 변경해 나간다.
    4. 단, 엣지를 'weak'으로 변경했을 때 해당 엣지가 속한 커뮤니티의 연결성(connectivity)이 끊어지면 안 된다 (커뮤니티 멤버들은 항상 'strong' 엣지들로만 연결된 경로를 유지해야 함).
    5. 더 이상 STC 위반이 없거나, 커뮤니티 연결성을 해치지 않고는 'weak'으로 변경할 엣지가 없을 때까지 반복한다.

#### `Pathfinder` 모듈
- **`find_meaningful_path(graph, start_node_id, end_node_id)`**: 가중치를 고려한 최단 경로를 탐색한다.
  - **Input**: `graph`, 시작 노드 ID, 끝 노드 ID
  - **Output**: 노드 ID의 배열 (경로)
  - **Logic**:
    1. 다익스트라(Dijkstra) 또는 A* 알고리즘을 활용한다.
    2. 엣지의 가중치(비용)를 `strength`에 따라 다르게 설정한다: `strength: 'strong'` 이면 비용 1, `strength: 'weak'` 이면 비용 10 (비용은 조절 가능).
    3. 시작 노드에서 끝 노드까지 가장 낮은 총비용을 가진 경로를 찾아 반환한다.

### 3. 시각화 명세
- 프론트엔드 또는 시각화 라이브러리는 엣지(선)를 렌더링할 때 `strength` 속성을 확인하여 아래와 같이 다르게 그린다.
  - `strength: 'strong'`: **굵은 실선** (예: `stroke-width: 3px`)
  - `strength: 'weak'`: **얇은 점선** (예: `stroke-width: 1px`, `stroke-dasharray: 5, 5`)