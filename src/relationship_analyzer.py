import re
import numpy as np
from typing import Dict, List, Set, Tuple, Optional
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class RelationshipAnalyzer:
    """두 인스타그램 사용자 간의 관계를 분석하는 클래스"""
    
    def __init__(self):
        self.weights = {
            'mutual_followers': 0.3,
            'mutual_following': 0.25,
            'profile_similarity': 0.2,
            'content_similarity': 0.15,
            'interaction_indicators': 0.1
        }
    
    def analyze_relationship(self, user1_data: Dict, user2_data: Dict) -> Dict:
        """
        두 사용자 간의 전체 관계 분석
        
        Args:
            user1_data (Dict): 첫 번째 사용자 데이터
            user2_data (Dict): 두 번째 사용자 데이터
            
        Returns:
            Dict: 분석 결과
        """
        try:
            # 각 지표별 점수 계산
            mutual_followers_score = self.calculate_mutual_followers_score(
                user1_data, user2_data
            )
            
            mutual_following_score = self.calculate_mutual_following_score(
                user1_data, user2_data
            )
            
            profile_similarity_score = self.calculate_profile_similarity(
                user1_data['profile'], user2_data['profile']
            )
            
            content_similarity_score = self.calculate_content_similarity(
                user1_data.get('posts', []), user2_data.get('posts', [])
            )
            
            interaction_score = self.calculate_interaction_indicators(
                user1_data, user2_data
            )
            
            # 가중 평균으로 총 점수 계산
            total_score = (
                mutual_followers_score * self.weights['mutual_followers'] +
                mutual_following_score * self.weights['mutual_following'] +
                profile_similarity_score * self.weights['profile_similarity'] +
                content_similarity_score * self.weights['content_similarity'] +
                interaction_score * self.weights['interaction_indicators']
            )
            
            # 관계 강도 분류
            relationship_level = self.classify_relationship(total_score)
            
            result = {
                'total_score': round(total_score, 3),
                'relationship_level': relationship_level,
                'detailed_scores': {
                    'mutual_followers': round(mutual_followers_score, 3),
                    'mutual_following': round(mutual_following_score, 3),
                    'profile_similarity': round(profile_similarity_score, 3),
                    'content_similarity': round(content_similarity_score, 3),
                    'interaction_indicators': round(interaction_score, 3)
                },
                'mutual_connections': self.get_mutual_connections(user1_data, user2_data),
                'analysis_summary': self.generate_analysis_summary(
                    user1_data, user2_data, total_score
                )
            }
            
            logger.info(f"관계 분석 완료: {user1_data['profile'].get('username', 'Unknown')} - {user2_data['profile'].get('username', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"관계 분석 실패: {e}")
            return {'error': str(e)}
    
    def calculate_mutual_followers_score(self, user1_data: Dict, user2_data: Dict) -> float:
        """공통 팔로워 기반 점수 계산"""
        try:
            followers1 = user1_data.get('followers', set())
            followers2 = user2_data.get('followers', set())
            
            if not followers1 or not followers2:
                return 0.0
            
            mutual_followers = followers1.intersection(followers2)
            mutual_count = len(mutual_followers)
            
            # 공통 팔로워 수에 따른 점수 (로그 스케일 적용)
            if mutual_count == 0:
                return 0.0
            elif mutual_count <= 5:
                return mutual_count * 0.2
            elif mutual_count <= 20:
                return 1.0 + (mutual_count - 5) * 0.05
            else:
                return min(2.0, 1.75 + np.log10(mutual_count - 20))
                
        except Exception as e:
            logger.error(f"공통 팔로워 점수 계산 실패: {e}")
            return 0.0
    
    def calculate_mutual_following_score(self, user1_data: Dict, user2_data: Dict) -> float:
        """공통 팔로잉 기반 점수 계산"""
        try:
            following1 = user1_data.get('following', set())
            following2 = user2_data.get('following', set())
            
            if not following1 or not following2:
                return 0.0
            
            mutual_following = following1.intersection(following2)
            mutual_count = len(mutual_following)
            
            # 공통 팔로잉 수에 따른 점수
            if mutual_count == 0:
                return 0.0
            elif mutual_count <= 10:
                return mutual_count * 0.15
            elif mutual_count <= 50:
                return 1.5 + (mutual_count - 10) * 0.025
            else:
                return min(2.5, 2.5 + np.log10(mutual_count - 50))
                
        except Exception as e:
            logger.error(f"공통 팔로잉 점수 계산 실패: {e}")
            return 0.0
    
    def calculate_profile_similarity(self, profile1: Dict, profile2: Dict) -> float:
        """프로필 유사도 기반 점수 계산"""
        try:
            score = 0.0
            
            # 이름 유사도
            name1 = profile1.get('full_name', '').lower()
            name2 = profile2.get('full_name', '').lower()
            if name1 and name2:
                score += self.calculate_text_similarity(name1, name2) * 0.3
            
            # 바이오 유사도
            bio1 = profile1.get('biography', '').lower()
            bio2 = profile2.get('biography', '').lower()
            if bio1 and bio2:
                bio_similarity = self.calculate_text_similarity(bio1, bio2)
                score += bio_similarity * 0.4
                
                # 공통 키워드 보너스
                common_keywords = self.extract_common_keywords(bio1, bio2)
                score += min(0.5, len(common_keywords) * 0.1)
            
            # 비즈니스 계정 여부
            if (profile1.get('business_account') == profile2.get('business_account') and 
                profile1.get('business_account')):
                score += 0.2
            
            # 인증 계정 여부
            if (profile1.get('is_verified') == profile2.get('is_verified') and 
                profile1.get('is_verified')):
                score += 0.1
            
            return min(3.0, score)
            
        except Exception as e:
            logger.error(f"프로필 유사도 계산 실패: {e}")
            return 0.0
    
    def calculate_content_similarity(self, posts1: List[Dict], posts2: List[Dict]) -> float:
        """게시물 콘텐츠 유사도 계산"""
        try:
            if not posts1 or not posts2:
                return 0.0
            
            score = 0.0
            
            # 해시태그 유사도
            hashtags1 = set()
            hashtags2 = set()
            
            for post in posts1:
                hashtags1.update(post.get('hashtags', []))
            
            for post in posts2:
                hashtags2.update(post.get('hashtags', []))
            
            if hashtags1 and hashtags2:
                common_hashtags = hashtags1.intersection(hashtags2)
                hashtag_score = len(common_hashtags) / max(len(hashtags1), len(hashtags2))
                score += hashtag_score * 1.5
            
            # 멘션 유사도
            mentions1 = set()
            mentions2 = set()
            
            for post in posts1:
                mentions1.update(post.get('mentions', []))
            
            for post in posts2:
                mentions2.update(post.get('mentions', []))
            
            if mentions1 and mentions2:
                common_mentions = mentions1.intersection(mentions2)
                mention_score = len(common_mentions) / max(len(mentions1), len(mentions2))
                score += mention_score * 2.0
            
            # 위치 유사도
            locations1 = {post.get('location') for post in posts1 if post.get('location')}
            locations2 = {post.get('location') for post in posts2 if post.get('location')}
            
            if locations1 and locations2:
                common_locations = locations1.intersection(locations2)
                if common_locations:
                    score += len(common_locations) * 0.5
            
            return min(3.0, score)
            
        except Exception as e:
            logger.error(f"콘텐츠 유사도 계산 실패: {e}")
            return 0.0
    
    def calculate_interaction_indicators(self, user1_data: Dict, user2_data: Dict) -> float:
        """상호작용 지표 계산"""
        try:
            score = 0.0
            
            user1_posts = user1_data.get('posts', [])
            user2_posts = user2_data.get('posts', [])
            user2_username = user2_data['profile'].get('username', '')
            user1_username = user1_data['profile'].get('username', '')
            
            # user1의 게시물에서 user2 멘션 확인
            for post in user1_posts:
                mentions = post.get('mentions', [])
                if user2_username in mentions:
                    score += 1.0
            
            # user2의 게시물에서 user1 멘션 확인
            for post in user2_posts:
                mentions = post.get('mentions', [])
                if user1_username in mentions:
                    score += 1.0
            
            return min(2.0, score)
            
        except Exception as e:
            logger.error(f"상호작용 지표 계산 실패: {e}")
            return 0.0
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간의 코사인 유사도 계산"""
        try:
            if not text1 or not text2:
                return 0.0
            
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            return float(similarity[0][0])
            
        except Exception as e:
            logger.error(f"텍스트 유사도 계산 실패: {e}")
            return 0.0
    
    def extract_common_keywords(self, text1: str, text2: str) -> Set[str]:
        """두 텍스트에서 공통 키워드 추출"""
        try:
            # 한국어 및 영어 키워드 패턴
            pattern = r'[가-힣a-zA-Z]{2,}'
            
            words1 = set(re.findall(pattern, text1.lower()))
            words2 = set(re.findall(pattern, text2.lower()))
            
            # 불용어 제거 (간단한 예시)
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                         'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through'}
            
            words1 = words1 - stop_words
            words2 = words2 - stop_words
            
            return words1.intersection(words2)
            
        except Exception as e:
            logger.error(f"공통 키워드 추출 실패: {e}")
            return set()
    
    def get_mutual_connections(self, user1_data: Dict, user2_data: Dict) -> Dict:
        """공통 연결 정보 반환"""
        try:
            mutual_followers = user1_data.get('followers', set()).intersection(
                user2_data.get('followers', set())
            )
            
            mutual_following = user1_data.get('following', set()).intersection(
                user2_data.get('following', set())
            )
            
            return {
                'mutual_followers': list(mutual_followers)[:10],  # 상위 10명만
                'mutual_followers_count': len(mutual_followers),
                'mutual_following': list(mutual_following)[:10],  # 상위 10명만
                'mutual_following_count': len(mutual_following)
            }
            
        except Exception as e:
            logger.error(f"공통 연결 정보 추출 실패: {e}")
            return {}
    
    def classify_relationship(self, score: float) -> str:
        """점수에 따른 관계 강도 분류"""
        if score >= 2.5:
            return "매우 가까운 관계"
        elif score >= 2.0:
            return "가까운 관계"
        elif score >= 1.5:
            return "어느 정도 아는 관계"
        elif score >= 1.0:
            return "약간 연결된 관계"
        elif score >= 0.5:
            return "희미한 연결"
        else:
            return "연결점이 거의 없음"
    
    def generate_analysis_summary(self, user1_data: Dict, user2_data: Dict, score: float) -> str:
        """분석 결과 요약 생성"""
        try:
            user1_name = user1_data['profile'].get('username', 'User1')
            user2_name = user2_data['profile'].get('username', 'User2')
            
            mutual_followers_count = len(
                user1_data.get('followers', set()).intersection(
                    user2_data.get('followers', set())
                )
            )
            
            mutual_following_count = len(
                user1_data.get('following', set()).intersection(
                    user2_data.get('following', set())
                )
            )
            
            summary = f"""
            {user1_name}과(와) {user2_name}의 관계 분석 결과:
            
            • 전체 친밀도 점수: {score:.2f}/3.0
            • 관계 수준: {self.classify_relationship(score)}
            • 공통 팔로워: {mutual_followers_count}명
            • 공통 팔로잉: {mutual_following_count}명
            
            주요 연결 요인:
            """
            
            if mutual_followers_count > 0:
                summary += f"\n- {mutual_followers_count}명의 공통 팔로워가 있어 같은 커뮤니티에 속할 가능성이 높습니다"
            
            if mutual_following_count > 0:
                summary += f"\n- {mutual_following_count}명을 공통으로 팔로우하여 관심사가 비슷합니다"
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"분석 요약 생성 실패: {e}")
            return "분석 요약을 생성할 수 없습니다."


# 편의 함수들
def analyze_relationship(user1_data: Dict, user2_data: Dict) -> Dict:
    """간단한 관계 분석 함수"""
    analyzer = RelationshipAnalyzer()
    return analyzer.analyze_relationship(user1_data, user2_data)

def calculate_follow_score(user1_data: Dict, user2_data: Dict) -> float:
    """팔로우 관계 점수만 계산"""
    analyzer = RelationshipAnalyzer()
    return (analyzer.calculate_mutual_followers_score(user1_data, user2_data) +
            analyzer.calculate_mutual_following_score(user1_data, user2_data)) / 2

def calculate_profile_similarity(profile1: Dict, profile2: Dict) -> float:
    """프로필 유사도만 계산"""
    analyzer = RelationshipAnalyzer()
    return analyzer.calculate_profile_similarity(profile1, profile2)

def calculate_interaction_score(user1_data: Dict, user2_data: Dict) -> float:
    """상호작용 점수만 계산"""
    analyzer = RelationshipAnalyzer()
    return analyzer.calculate_interaction_indicators(user1_data, user2_data)

def calculate_total_score(user1_data: Dict, user2_data: Dict) -> float:
    """전체 점수만 계산"""
    analyzer = RelationshipAnalyzer()
    result = analyzer.analyze_relationship(user1_data, user2_data)
    return result.get('total_score', 0.0)