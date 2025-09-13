#!/usr/bin/env python3
"""
Instagram 관계 분석기 테스트
"""

import pytest
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.relationship_analyzer import RelationshipAnalyzer


class TestRelationshipAnalyzer:
    """관계 분석기 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메소드 실행 전 호출"""
        self.analyzer = RelationshipAnalyzer()
        
        # 테스트 데이터 준비
        self.user1_data = {
            'profile': {
                'username': 'test_user1',
                'full_name': 'Test User One',
                'biography': '안녕하세요 서울대학교 컴퓨터공학과 재학생입니다',
                'followers': 1000,
                'followees': 500,
                'posts_count': 100,
                'is_private': False,
                'is_verified': False,
                'business_account': False
            },
            'followers': {'common_user1', 'common_user2', 'follower1', 'follower2'},
            'following': {'common_follow1', 'common_follow2', 'follow1', 'follow2'},
            'posts': [
                {
                    'shortcode': 'ABC123',
                    'caption': '서울대학교에서 공부 중 #서울대 #컴공 #프로그래밍',
                    'hashtags': ['서울대', '컴공', '프로그래밍'],
                    'mentions': ['test_user2'],
                    'location': '서울대학교'
                }
            ]
        }
        
        self.user2_data = {
            'profile': {
                'username': 'test_user2',
                'full_name': 'Test User Two',
                'biography': '서울대학교 컴퓨터공학과 학생입니다',
                'followers': 1200,
                'followees': 600,
                'posts_count': 80,
                'is_private': False,
                'is_verified': False,
                'business_account': False
            },
            'followers': {'common_user1', 'common_user2', 'follower3', 'follower4'},
            'following': {'common_follow1', 'common_follow2', 'follow3', 'follow4'},
            'posts': [
                {
                    'shortcode': 'DEF456',
                    'caption': '컴공 과제 완료! #서울대 #컴공 #과제',
                    'hashtags': ['서울대', '컴공', '과제'],
                    'mentions': ['test_user1'],
                    'location': '서울대학교'
                }
            ]
        }
    
    def test_calculate_mutual_followers_score(self):
        """공통 팔로워 점수 계산 테스트"""
        score = self.analyzer.calculate_mutual_followers_score(self.user1_data, self.user2_data)
        
        # 2명의 공통 팔로워가 있으므로 0.4 점수 예상
        assert score == 0.4
        assert isinstance(score, float)
    
    def test_calculate_mutual_following_score(self):
        """공통 팔로잉 점수 계산 테스트"""
        score = self.analyzer.calculate_mutual_following_score(self.user1_data, self.user2_data)
        
        # 2명의 공통 팔로잉이 있으므로 0.3 점수 예상
        assert score == 0.3
        assert isinstance(score, float)
    
    def test_calculate_profile_similarity(self):
        """프로필 유사도 계산 테스트"""
        profile1 = self.user1_data['profile']
        profile2 = self.user2_data['profile']
        
        score = self.analyzer.calculate_profile_similarity(profile1, profile2)
        
        # 비슷한 바이오그래피로 인해 0보다 큰 점수 예상
        assert score > 0
        assert isinstance(score, float)
        assert score <= 3.0  # 최대 점수 확인
    
    def test_calculate_content_similarity(self):
        """콘텐츠 유사도 계산 테스트"""
        posts1 = self.user1_data['posts']
        posts2 = self.user2_data['posts']
        
        score = self.analyzer.calculate_content_similarity(posts1, posts2)
        
        # 공통 해시태그와 위치로 인해 0보다 큰 점수 예상
        assert score > 0
        assert isinstance(score, float)
        assert score <= 3.0  # 최대 점수 확인
    
    def test_calculate_interaction_indicators(self):
        """상호작용 지표 계산 테스트"""
        score = self.analyzer.calculate_interaction_indicators(self.user1_data, self.user2_data)
        
        # 서로 멘션이 있으므로 2.0 점수 예상
        assert score == 2.0
        assert isinstance(score, float)
    
    def test_extract_common_keywords(self):
        """공통 키워드 추출 테스트"""
        text1 = "서울대학교 컴퓨터공학과 재학생입니다"
        text2 = "서울대학교 컴퓨터공학과 학생입니다"
        
        keywords = self.analyzer.extract_common_keywords(text1, text2)
        
        assert '서울대학교' in keywords
        assert '컴퓨터공학과' in keywords
        assert isinstance(keywords, set)
    
    def test_get_mutual_connections(self):
        """공통 연결 정보 확인 테스트"""
        connections = self.analyzer.get_mutual_connections(self.user1_data, self.user2_data)
        
        assert 'mutual_followers' in connections
        assert 'mutual_following' in connections
        assert 'mutual_followers_count' in connections
        assert 'mutual_following_count' in connections
        
        assert connections['mutual_followers_count'] == 2
        assert connections['mutual_following_count'] == 2
        assert 'common_user1' in connections['mutual_followers']
        assert 'common_follow1' in connections['mutual_following']
    
    def test_classify_relationship(self):
        """관계 분류 테스트"""
        # 다양한 점수에 대한 분류 테스트
        assert self.analyzer.classify_relationship(2.8) == "매우 가까운 관계"
        assert self.analyzer.classify_relationship(2.2) == "가까운 관계"
        assert self.analyzer.classify_relationship(1.7) == "어느 정도 아는 관계"
        assert self.analyzer.classify_relationship(1.3) == "약간 연결된 관계"
        assert self.analyzer.classify_relationship(0.8) == "희미한 연결"
        assert self.analyzer.classify_relationship(0.2) == "연결점이 거의 없음"
    
    def test_analyze_relationship(self):
        """전체 관계 분석 테스트"""
        result = self.analyzer.analyze_relationship(self.user1_data, self.user2_data)
        
        # 결과 구조 확인
        assert 'total_score' in result
        assert 'relationship_level' in result
        assert 'detailed_scores' in result
        assert 'mutual_connections' in result
        assert 'analysis_summary' in result
        
        # 점수가 유효한 범위 내에 있는지 확인
        assert 0 <= result['total_score'] <= 3.0
        
        # 세부 점수들 확인
        detailed = result['detailed_scores']
        assert 'mutual_followers' in detailed
        assert 'mutual_following' in detailed
        assert 'profile_similarity' in detailed
        assert 'content_similarity' in detailed
        assert 'interaction_indicators' in detailed
        
        # 모든 세부 점수가 0 이상이어야 함
        for score in detailed.values():
            assert score >= 0
    
    def test_empty_data_handling(self):
        """빈 데이터 처리 테스트"""
        empty_user = {
            'profile': {},
            'followers': set(),
            'following': set(),
            'posts': []
        }
        
        result = self.analyzer.analyze_relationship(empty_user, empty_user)
        
        # 에러 없이 처리되고 0점이 나와야 함
        assert result['total_score'] == 0.0
        assert result['relationship_level'] == "연결점이 거의 없음"
    
    def test_text_similarity(self):
        """텍스트 유사도 계산 테스트"""
        text1 = "안녕하세요 서울대학교 학생입니다"
        text2 = "안녕하세요 서울대학교 재학생입니다"
        
        similarity = self.analyzer.calculate_text_similarity(text1, text2)
        
        assert 0 <= similarity <= 1.0
        assert similarity > 0.5  # 유사한 텍스트이므로 0.5보다 커야 함
    
    def test_weights_sum(self):
        """가중치 합계가 1인지 확인"""
        weights_sum = sum(self.analyzer.weights.values())
        assert abs(weights_sum - 1.0) < 0.001  # 부동소수점 오차 고려


if __name__ == '__main__':
    # 개별 테스트 실행 가능
    pytest.main([__file__, '-v'])