# Instagram 관계 분석기

![Status](https://img.shields.io/badge/Status-완료-brightgreen.svg)
![Language](https://img.shields.io/badge/Python-3.12-blue.svg)
![Framework](https://img.shields.io/badge/Flask-3.1.2-green.svg)

두 Instagram 사용자의 공개 정보를 분석하여 관계의 친밀도를 측정하는 웹 애플리케이션입니다.

## 🚀 실행 중인 애플리케이션

**📱 [Instagram 관계 분석기 실행하기](https://5000-ifbmhjzo3vvyb0gyeidwg-6532622b.e2b.dev/)**

## ✨ 주요 기능

### 📊 관계 분석 지표
- **공통 팔로워 분석**: 두 사용자의 공통 팔로워 수와 영향력 평가
- **공통 팔로잉 분석**: 공통으로 팔로우하는 계정을 통한 관심사 유사성 측정
- **프로필 유사도**: 이름, 바이오그래피, 키워드 분석을 통한 프로필 연관성
- **콘텐츠 유사도**: 해시태그, 멘션, 위치 정보를 통한 콘텐츠 연관성
- **상호작용 지표**: 서로 간의 멘션 및 상호작용 빈도 측정

### 🎯 분석 결과
- **0-3점 친밀도 점수**: 정량적 관계 강도 측정
- **6단계 관계 분류**: 매우 가까운 관계부터 연결점이 거의 없음까지
- **상세 분석 리포트**: 각 지표별 세부 점수 및 근거 제시
- **시각적 결과 표시**: 직관적인 차트와 그래프로 결과 제공

### 💻 사용자 경험
- **반응형 웹 인터페이스**: 모바일/데스크톱 최적화
- **실시간 진행 상황**: 분석 과정을 단계별로 표시
- **캐시 시스템**: 빠른 재분석을 위한 데이터 캐싱
- **에러 처리**: 친화적인 오류 메시지 및 복구 안내

## 🏗️ 기술 스택

### Backend
- **Python 3.12**: 메인 개발 언어
- **Flask 3.1.2**: 웹 프레임워크
- **Instaloader 4.14.2**: Instagram 데이터 수집
- **scikit-learn**: 텍스트 유사도 계산
- **Supervisor**: 프로세스 관리

### Frontend  
- **HTML5/CSS3**: 마크업 및 스타일링
- **JavaScript ES6**: 동적 인터페이스
- **Bootstrap 5**: UI 컴포넌트 및 반응형 디자인
- **Bootstrap Icons**: 아이콘 시스템

### DevOps & Testing
- **pytest**: 테스트 프레임워크
- **Git**: 버전 관리
- **환경변수**: 설정 관리

## 📋 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정 (선택사항)
```bash
cp .env.example .env
# .env 파일을 편집하여 Instagram 로그인 정보 설정 (공개 데이터만 사용할 경우 불필요)
```

### 3. 애플리케이션 실행

#### 개발 모드
```bash
python3 app.py
```

#### 프로덕션 모드 (Supervisor 사용)
```bash
supervisord -c supervisord.conf
supervisorctl -c supervisord.conf status
```

### 4. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 🧪 테스트

```bash
# 전체 테스트 실행
python3 -m pytest tests/ -v

# 특정 모듈 테스트
python3 -m pytest tests/test_relationship_analyzer.py -v
python3 -m pytest tests/test_data_collector.py -v
```

## 📁 프로젝트 구조

```
instagram-analyzer/
├── app.py                          # 메인 Flask 애플리케이션
├── src/
│   ├── data_collector.py           # Instagram 데이터 수집 모듈
│   └── relationship_analyzer.py    # 관계 분석 알고리즘
├── templates/
│   ├── index.html                  # 메인 페이지
│   └── error.html                  # 에러 페이지
├── static/
│   ├── css/style.css              # 스타일시트
│   └── js/app.js                  # JavaScript 로직
├── tests/
│   ├── test_data_collector.py     # 데이터 수집 테스트
│   ├── test_relationship_analyzer.py # 관계 분석 테스트
│   └── test_instaloader.py        # Instagram API 테스트
├── logs/                          # 애플리케이션 로그
├── cache/                         # 데이터 캐시
├── supervisord.conf               # Supervisor 설정
├── ecosystem.config.js            # PM2 설정 (선택사항)
├── requirements.txt               # Python 의존성
└── README.md                      # 프로젝트 문서
```

## 🔍 사용법

### 1. 사용자명 입력
- 분석하려는 두 Instagram 사용자의 username을 입력합니다
- @는 제외하고 username만 입력하세요

### 2. 분석 시작
- "관계 분석 시작" 버튼을 클릭합니다
- 분석 진행 상황이 실시간으로 표시됩니다

### 3. 결과 확인
- 친밀도 점수 (0-3점)
- 관계 수준 분류
- 세부 분석 점수
- 공통 연결 정보
- 분석 요약 리포트

## ⚠️ 주의사항

### 데이터 수집 제한사항
- **공개 계정만 분석 가능**: 비공개 계정은 데이터 수집이 불가능합니다
- **Instagram 이용 약관 준수**: 공개 정보만을 사용하며 개인정보를 보호합니다
- **Rate Limiting**: Instagram API 제한을 준수하여 안전한 데이터 수집을 수행합니다

### 개인정보 보호
- 분석 결과는 서버에 저장되지 않습니다
- 수집된 데이터는 임시 캐시에만 보관됩니다
- 사용자 개인정보 보호 정책을 엄격히 준수합니다

## 🎯 분석 알고리즘

### 점수 계산 방식

1. **공통 팔로워 (30% 가중치)**
   - 공통 팔로워 수에 따른 로그 스케일 점수
   - 1-5명: 선형 증가, 5명 이상: 로그 스케일

2. **공통 팔로잉 (25% 가중치)**  
   - 공통으로 팔로우하는 계정 수 분석
   - 관심사 유사성의 지표로 활용

3. **프로필 유사도 (20% 가중치)**
   - TF-IDF를 이용한 바이오그래피 텍스트 유사도
   - 공통 키워드 추출 및 분석
   - 계정 유형 (비즈니스, 인증 여부) 비교

4. **콘텐츠 유사도 (15% 가중치)**
   - 해시태그 중복도 분석
   - 공통 위치 정보 확인
   - 게시물 패턴 분석

5. **상호작용 지표 (10% 가중치)**
   - 서로 간의 멘션 빈도
   - 상호작용 패턴 분석

### 관계 수준 분류

| 점수 범위 | 관계 수준 | 설명 |
|----------|----------|------|
| 2.5-3.0 | 매우 가까운 관계 | 강한 연결성과 높은 상호작용 |
| 2.0-2.4 | 가까운 관계 | 여러 공통점을 가진 친한 사이 |
| 1.5-1.9 | 어느 정도 아는 관계 | 몇 가지 공통점이 있는 지인 |
| 1.0-1.4 | 약간 연결된 관계 | 미약한 연결고리가 존재 |
| 0.5-0.9 | 희미한 연결 | 최소한의 공통점만 존재 |
| 0.0-0.4 | 연결점이 거의 없음 | 거의 관계가 없음 |

## 🔧 개발 정보

### 개발 환경
- Python 3.12+
- 모던 웹 브라우저 (Chrome, Firefox, Safari, Edge)
- 인터넷 연결 필요

### 성능 최적화
- 데이터 캐싱으로 반복 분석 시간 단축
- 비동기 처리로 사용자 경험 개선
- 메모리 효율적인 데이터 구조 사용

### 확장 가능성
- 다른 SNS 플랫폼 지원 추가 가능
- 더 정교한 ML 알고리즘 적용 가능
- API 서비스로 확장 가능

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다. Instagram의 이용 약관을 준수하며 사용해주세요.

## 🤝 기여하기

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

---

**📧 문의사항이 있으시면 언제든지 연락주세요!**
