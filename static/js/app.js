/**
 * Instagram 관계 분석기 JavaScript
 */

// DOM이 로드되면 실행
document.addEventListener('DOMContentLoaded', function() {
    const analysisForm = document.getElementById('analysisForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const progressContainer = document.getElementById('progressContainer');
    const resultContainer = document.getElementById('resultContainer');
    
    // 폼 제출 이벤트 처리
    analysisForm.addEventListener('submit', function(e) {
        e.preventDefault();
        startAnalysis();
    });
    
    // 분석 시작 함수
    async function startAnalysis() {
        const username1 = document.getElementById('username1').value.trim();
        const username2 = document.getElementById('username2').value.trim();
        
        // 입력 검증
        if (!username1 || !username2) {
            showAlert('두 사용자명을 모두 입력해주세요.', 'danger');
            return;
        }
        
        if (username1 === username2) {
            showAlert('같은 사용자를 비교할 수 없습니다.', 'warning');
            return;
        }
        
        // UI 상태 변경
        setLoadingState(true);
        showProgress();
        hideResult();
        
        try {
            // 분석 요청
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username1: username1,
                    username2: username2
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '분석 요청이 실패했습니다.');
            }
            
            const result = await response.json();
            displayResult(result);
            
        } catch (error) {
            console.error('분석 오류:', error);
            showAlert(error.message, 'danger');
        } finally {
            setLoadingState(false);
            hideProgress();
        }
    }
    
    // 로딩 상태 설정
    function setLoadingState(isLoading) {
        analyzeBtn.disabled = isLoading;
        
        if (isLoading) {
            analyzeBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                분석 중...
            `;
        } else {
            analyzeBtn.innerHTML = `
                <i class="bi bi-graph-up"></i> 관계 분석 시작
            `;
        }
    }
    
    // 진행 상황 표시
    function showProgress() {
        progressContainer.style.display = 'block';
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        // 진행 상황 애니메이션
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 90) progress = 90;
            
            progressBar.style.width = progress + '%';
            
            // 진행 단계별 메시지
            if (progress < 25) {
                progressText.textContent = '사용자 정보 수집 중...';
            } else if (progress < 50) {
                progressText.textContent = '팔로우 데이터 분석 중...';
            } else if (progress < 75) {
                progressText.textContent = '프로필 비교 중...';
            } else {
                progressText.textContent = '관계 점수 계산 중...';
            }
        }, 500);
        
        // 완료 시 정리
        setTimeout(() => {
            clearInterval(interval);
            progressBar.style.width = '100%';
            progressText.textContent = '분석 완료!';
        }, 3000);
    }
    
    // 진행 상황 숨김
    function hideProgress() {
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 1000);
    }
    
    // 결과 표시
    function displayResult(result) {
        const { user1, user2, analysis } = result;
        
        // 사용자 정보 표시
        document.getElementById('user1Info').textContent = `@${user1.username}`;
        document.getElementById('user1Details').innerHTML = `
            ${user1.full_name || user1.username}<br>
            팔로워: ${formatNumber(user1.followers_count)} | 
            팔로잉: ${formatNumber(user1.following_count)} | 
            게시물: ${formatNumber(user1.posts_count)}
        `;
        
        document.getElementById('user2Info').textContent = `@${user2.username}`;
        document.getElementById('user2Details').innerHTML = `
            ${user2.full_name || user2.username}<br>
            팔로워: ${formatNumber(user2.followers_count)} | 
            팔로잉: ${formatNumber(user2.following_count)} | 
            게시물: ${formatNumber(user2.posts_count)}
        `;
        
        // 총 점수 및 관계 수준 표시
        document.getElementById('totalScore').textContent = analysis.total_score.toFixed(1);
        document.getElementById('relationshipLevel').textContent = analysis.relationship_level;
        
        // 점수 원형 색상 설정
        const scoreCircle = document.querySelector('.score-circle');
        setScoreCircleColor(scoreCircle, analysis.total_score);
        
        // 세부 점수 표시
        displayDetailedScores(analysis.detailed_scores);
        
        // 공통 연결 표시
        displayMutualConnections(analysis.mutual_connections);
        
        // 분석 요약 표시
        document.getElementById('analysisSummary').textContent = analysis.analysis_summary;
        
        // 결과 컨테이너 표시 (애니메이션 효과)
        resultContainer.style.display = 'block';
        resultContainer.classList.add('fade-in-up');
        
        // 결과로 스크롤
        setTimeout(() => {
            resultContainer.scrollIntoView({ behavior: 'smooth' });
        }, 300);
    }
    
    // 세부 점수 표시
    function displayDetailedScores(scores) {
        const scoreItems = {
            'mutualFollowers': scores.mutual_followers,
            'mutualFollowing': scores.mutual_following,
            'profileSimilarity': scores.profile_similarity,
            'contentSimilarity': scores.content_similarity,
            'interaction': scores.interaction_indicators
        };
        
        // 각 점수에 대해 애니메이션 효과로 표시
        Object.entries(scoreItems).forEach(([key, value], index) => {
            setTimeout(() => {
                const scoreElement = document.getElementById(`${key}Score`);
                const barElement = document.getElementById(`${key}Bar`);
                
                if (scoreElement && barElement) {
                    scoreElement.textContent = value.toFixed(1);
                    
                    // 최대 점수에 따른 퍼센트 계산 (최대 3.0 기준)
                    const percentage = (value / 3.0) * 100;
                    barElement.style.width = Math.min(100, percentage) + '%';
                    
                    // 점수에 따른 색상 변경
                    if (value >= 2.0) {
                        barElement.style.background = 'linear-gradient(90deg, #28a745, #20c997)';
                    } else if (value >= 1.0) {
                        barElement.style.background = 'linear-gradient(90deg, #ffc107, #fd7e14)';
                    } else {
                        barElement.style.background = 'linear-gradient(90deg, #dc3545, #c82333)';
                    }
                }
            }, index * 200);
        });
    }
    
    // 공통 연결 표시
    function displayMutualConnections(connections) {
        const followersList = document.getElementById('mutualFollowersList');
        const followingList = document.getElementById('mutualFollowingList');
        
        // 공통 팔로워 표시
        if (connections.mutual_followers && connections.mutual_followers.length > 0) {
            followersList.innerHTML = connections.mutual_followers
                .map(username => `<span class="mutual-user">@${username}</span>`)
                .join('');
            
            if (connections.mutual_followers_count > connections.mutual_followers.length) {
                followersList.innerHTML += `<span class="text-muted">... 외 ${connections.mutual_followers_count - connections.mutual_followers.length}명</span>`;
            }
        } else {
            followersList.innerHTML = '<span class="text-muted">공통 팔로워가 없습니다.</span>';
        }
        
        // 공통 팔로잉 표시
        if (connections.mutual_following && connections.mutual_following.length > 0) {
            followingList.innerHTML = connections.mutual_following
                .map(username => `<span class="mutual-user">@${username}</span>`)
                .join('');
            
            if (connections.mutual_following_count > connections.mutual_following.length) {
                followingList.innerHTML += `<span class="text-muted">... 외 ${connections.mutual_following_count - connections.mutual_following.length}명</span>`;
            }
        } else {
            followingList.innerHTML = '<span class="text-muted">공통으로 팔로우하는 사용자가 없습니다.</span>';
        }
    }
    
    // 점수 원형 색상 설정
    function setScoreCircleColor(element, score) {
        element.classList.remove('level-very-close', 'level-close', 'level-somewhat', 'level-weak', 'level-minimal', 'level-none');
        
        if (score >= 2.5) {
            element.classList.add('level-very-close');
        } else if (score >= 2.0) {
            element.classList.add('level-close');
        } else if (score >= 1.5) {
            element.classList.add('level-somewhat');
        } else if (score >= 1.0) {
            element.classList.add('level-weak');
        } else if (score >= 0.5) {
            element.classList.add('level-minimal');
        } else {
            element.classList.add('level-none');
        }
    }
    
    // 결과 숨김
    function hideResult() {
        resultContainer.style.display = 'none';
        resultContainer.classList.remove('fade-in-up');
    }
    
    // 알림 표시
    function showAlert(message, type = 'info') {
        // 기존 알림 제거
        const existingAlert = document.querySelector('.alert-dismissible');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        // 새 알림 생성
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // 폼 위에 삽입
        analysisForm.parentNode.insertBefore(alertDiv, analysisForm);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    // 숫자 포맷팅 (천 단위 콤마)
    function formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return num.toLocaleString();
    }
    
    // 엔터키 처리
    document.getElementById('username1').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('username2').focus();
        }
    });
    
    document.getElementById('username2').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analysisForm.dispatchEvent(new Event('submit'));
        }
    });
});