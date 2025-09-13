#!/usr/bin/env python3
"""
Instagram 관계 분석 웹 애플리케이션
두 Instagram 사용자 간의 관계를 공개 정보를 통해 분석합니다.
"""

from flask import Flask, render_template, request, jsonify, session
from src.data_collector import InstagramDataCollector
from src.relationship_analyzer import RelationshipAnalyzer
import os
import json
import logging
from datetime import datetime, timedelta
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# 전역 변수
collector = InstagramDataCollector(use_login=False)
analyzer = RelationshipAnalyzer()

# 캐시 디렉토리 설정
CACHE_DIR = 'cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(username):
    """사용자명을 위한 캐시 키 생성"""
    return hashlib.md5(username.encode()).hexdigest()

def is_cache_valid(cache_file, hours=24):
    """캐시 파일이 유효한지 확인 (기본 24시간)"""
    if not os.path.exists(cache_file):
        return False
    
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    return datetime.now() - file_time < timedelta(hours=hours)

def load_from_cache(username):
    """캐시에서 사용자 데이터 로드"""
    cache_key = get_cache_key(username)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if is_cache_valid(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"{username} 데이터를 캐시에서 로드했습니다.")
                return data
        except Exception as e:
            logger.error(f"캐시 로드 실패: {e}")
    
    return None

def save_to_cache(username, data):
    """사용자 데이터를 캐시에 저장"""
    cache_key = get_cache_key(username)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    try:
        # Set을 list로 변환하여 JSON 직렬화 가능하게 만듦
        cache_data = data.copy()
        cache_data['followers'] = list(data.get('followers', set()))
        cache_data['following'] = list(data.get('following', set()))
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"{username} 데이터를 캐시에 저장했습니다.")
    except Exception as e:
        logger.error(f"캐시 저장 실패: {e}")

def get_user_data(username):
    """사용자 데이터 가져오기 (캐시 우선)"""
    # 캐시에서 먼저 확인
    cached_data = load_from_cache(username)
    if cached_data:
        # list를 set으로 변환
        cached_data['followers'] = set(cached_data.get('followers', []))
        cached_data['following'] = set(cached_data.get('following', []))
        return cached_data
    
    # 캐시에 없으면 새로 수집
    logger.info(f"{username} 데이터를 새로 수집합니다.")
    data = collector.collect_user_data(username, include_posts=True)
    
    if data and data.get('profile'):
        save_to_cache(username, data)
        return data
    
    return None

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """관계 분석 실행"""
    try:
        data = request.get_json()
        username1 = data.get('username1', '').strip()
        username2 = data.get('username2', '').strip()
        
        if not username1 or not username2:
            return jsonify({'error': '두 사용자명을 모두 입력해주세요.'}), 400
        
        if username1 == username2:
            return jsonify({'error': '같은 사용자를 비교할 수 없습니다.'}), 400
        
        # 진행 상황 저장 (세션 사용)
        session['analysis_progress'] = {'current': 0, 'total': 4, 'status': '분석 시작'}
        
        # 첫 번째 사용자 데이터 수집
        session['analysis_progress'] = {'current': 1, 'total': 4, 'status': f'{username1} 데이터 수집 중...'}
        user1_data = get_user_data(username1)
        
        if not user1_data or not user1_data.get('profile'):
            return jsonify({'error': f'{username1} 사용자를 찾을 수 없거나 데이터를 수집할 수 없습니다.'}), 404
        
        # 두 번째 사용자 데이터 수집
        session['analysis_progress'] = {'current': 2, 'total': 4, 'status': f'{username2} 데이터 수집 중...'}
        user2_data = get_user_data(username2)
        
        if not user2_data or not user2_data.get('profile'):
            return jsonify({'error': f'{username2} 사용자를 찾을 수 없거나 데이터를 수집할 수 없습니다.'}), 404
        
        # 관계 분석 실행
        session['analysis_progress'] = {'current': 3, 'total': 4, 'status': '관계 분석 중...'}
        analysis_result = analyzer.analyze_relationship(user1_data, user2_data)
        
        if 'error' in analysis_result:
            return jsonify({'error': f'분석 실패: {analysis_result["error"]}'}), 500
        
        # 결과 정리
        session['analysis_progress'] = {'current': 4, 'total': 4, 'status': '분석 완료'}
        
        result = {
            'user1': {
                'username': user1_data['profile'].get('username'),
                'full_name': user1_data['profile'].get('full_name'),
                'followers_count': user1_data['profile'].get('followers'),
                'following_count': user1_data['profile'].get('followees'),
                'posts_count': user1_data['profile'].get('posts_count'),
                'is_private': user1_data['profile'].get('is_private')
            },
            'user2': {
                'username': user2_data['profile'].get('username'),
                'full_name': user2_data['profile'].get('full_name'),
                'followers_count': user2_data['profile'].get('followers'),
                'following_count': user2_data['profile'].get('followees'),
                'posts_count': user2_data['profile'].get('posts_count'),
                'is_private': user2_data['profile'].get('is_private')
            },
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"분석 완료: {username1} - {username2}, 점수: {analysis_result.get('total_score')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"분석 중 오류: {e}")
        return jsonify({'error': f'분석 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/progress')
def progress():
    """분석 진행 상황 확인"""
    progress = session.get('analysis_progress', {'current': 0, 'total': 4, 'status': '대기 중'})
    return jsonify(progress)

@app.route('/user/<username>')
def user_info(username):
    """개별 사용자 정보 조회"""
    try:
        user_data = get_user_data(username)
        
        if not user_data or not user_data.get('profile'):
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        # 간단한 사용자 정보만 반환
        result = {
            'profile': user_data['profile'],
            'followers_sample': list(user_data.get('followers', set()))[:10],
            'following_sample': list(user_data.get('following', set()))[:10],
            'recent_posts': user_data.get('posts', [])[:5]
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"사용자 정보 조회 실패: {e}")
        return jsonify({'error': f'사용자 정보를 가져올 수 없습니다: {str(e)}'}), 500

@app.route('/clear_cache')
def clear_cache():
    """캐시 삭제"""
    try:
        import shutil
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
            os.makedirs(CACHE_DIR, exist_ok=True)
        
        return jsonify({'message': '캐시가 삭제되었습니다.'})
    except Exception as e:
        return jsonify({'error': f'캐시 삭제 실패: {str(e)}'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='페이지를 찾을 수 없습니다.'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='내부 서버 오류가 발생했습니다.'), 500

if __name__ == '__main__':
    # 개발 환경에서는 디버그 모드 사용
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Instagram 관계 분석 애플리케이션 시작 (포트: {port})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)