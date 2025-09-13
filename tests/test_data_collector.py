#!/usr/bin/env python3
"""
Instagram 데이터 수집기 테스트
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collector import InstagramDataCollector


class TestInstagramDataCollector:
    """데이터 수집기 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메소드 실행 전 호출"""
        self.collector = InstagramDataCollector(use_login=False)
    
    @patch('instaloader.Profile.from_username')
    def test_get_profile_info_success(self, mock_profile):
        """프로필 정보 수집 성공 테스트"""
        # Mock 프로필 객체 설정
        mock_profile_obj = Mock()
        mock_profile_obj.username = 'test_user'
        mock_profile_obj.full_name = 'Test User'
        mock_profile_obj.biography = 'Test bio'
        mock_profile_obj.followers = 1000
        mock_profile_obj.followees = 500
        mock_profile_obj.mediacount = 100
        mock_profile_obj.is_private = False
        mock_profile_obj.is_verified = False
        mock_profile_obj.external_url = 'https://example.com'
        mock_profile_obj.profile_pic_url = 'https://example.com/pic.jpg'
        mock_profile_obj.is_business_account = False
        mock_profile_obj.business_category_name = None
        
        mock_profile.return_value = mock_profile_obj
        
        result = self.collector.get_profile_info('test_user')
        
        # 결과 검증
        assert result['username'] == 'test_user'
        assert result['full_name'] == 'Test User'
        assert result['biography'] == 'Test bio'
        assert result['followers'] == 1000
        assert result['followees'] == 500
        assert result['posts_count'] == 100
        assert result['is_private'] is False
        assert result['is_verified'] is False
        
        mock_profile.assert_called_once()
    
    @patch('instaloader.Profile.from_username')
    def test_get_profile_info_not_found(self, mock_profile):
        """존재하지 않는 사용자 테스트"""
        from instaloader.exceptions import ProfileNotExistsException
        
        mock_profile.side_effect = ProfileNotExistsException('Profile not found')
        
        result = self.collector.get_profile_info('nonexistent_user')
        
        # 빈 딕셔너리가 반환되어야 함
        assert result == {}
    
    @patch('instaloader.Profile.from_username')
    def test_get_followers_list_private_account(self, mock_profile):
        """비공개 계정 팔로워 수집 테스트"""
        mock_profile_obj = Mock()
        mock_profile_obj.is_private = True
        mock_profile.return_value = mock_profile_obj
        
        result = self.collector.get_followers_list('private_user')
        
        # 빈 set이 반환되어야 함
        assert result == set()
    
    @patch('instaloader.Profile.from_username')
    def test_get_followers_list_success(self, mock_profile):
        """팔로워 목록 수집 성공 테스트"""
        # Mock 팔로워 객체들
        mock_follower1 = Mock()
        mock_follower1.username = 'follower1'
        mock_follower2 = Mock()
        mock_follower2.username = 'follower2'
        
        mock_profile_obj = Mock()
        mock_profile_obj.is_private = False
        mock_profile_obj.get_followers.return_value = [mock_follower1, mock_follower2]
        mock_profile.return_value = mock_profile_obj
        
        result = self.collector.get_followers_list('test_user', limit=5)
        
        # 결과 검증
        assert isinstance(result, set)
        assert 'follower1' in result
        assert 'follower2' in result
        assert len(result) == 2
    
    @patch('instaloader.Profile.from_username')
    def test_get_following_list_success(self, mock_profile):
        """팔로잉 목록 수집 성공 테스트"""
        # Mock 팔로잉 객체들
        mock_followee1 = Mock()
        mock_followee1.username = 'followee1'
        mock_followee2 = Mock()
        mock_followee2.username = 'followee2'
        
        mock_profile_obj = Mock()
        mock_profile_obj.is_private = False
        mock_profile_obj.get_followees.return_value = [mock_followee1, mock_followee2]
        mock_profile.return_value = mock_profile_obj
        
        result = self.collector.get_following_list('test_user', limit=5)
        
        # 결과 검증
        assert isinstance(result, set)
        assert 'followee1' in result
        assert 'followee2' in result
        assert len(result) == 2
    
    @patch('instaloader.Profile.from_username')
    def test_get_recent_posts_success(self, mock_profile):
        """최근 게시물 수집 성공 테스트"""
        from datetime import datetime
        
        # Mock 게시물 객체
        mock_post = Mock()
        mock_post.shortcode = 'ABC123'
        mock_post.caption = 'Test caption #test'
        mock_post.likes = 100
        mock_post.comments = 10
        mock_post.date_utc = datetime.utcnow()
        mock_post.is_video = False
        mock_post.caption_hashtags = {'test'}
        mock_post.caption_mentions = {'mentioned_user'}
        mock_post.location = None
        
        mock_profile_obj = Mock()
        mock_profile_obj.is_private = False
        mock_profile_obj.get_posts.return_value = [mock_post]
        mock_profile.return_value = mock_profile_obj
        
        result = self.collector.get_recent_posts('test_user', limit=1)
        
        # 결과 검증
        assert len(result) == 1
        assert result[0]['shortcode'] == 'ABC123'
        assert result[0]['caption'] == 'Test caption #test'
        assert result[0]['likes'] == 100
        assert result[0]['comments'] == 10
        assert result[0]['is_video'] is False
        assert 'test' in result[0]['hashtags']
        assert 'mentioned_user' in result[0]['mentions']
    
    @patch.object(InstagramDataCollector, 'get_profile_info')
    @patch.object(InstagramDataCollector, 'get_followers_list')
    @patch.object(InstagramDataCollector, 'get_following_list')
    @patch.object(InstagramDataCollector, 'get_recent_posts')
    def test_collect_user_data_success(self, mock_posts, mock_following, mock_followers, mock_profile):
        """사용자 데이터 수집 통합 테스트"""
        # Mock 데이터 설정
        mock_profile.return_value = {
            'username': 'test_user',
            'full_name': 'Test User',
            'followers': 1000
        }
        mock_followers.return_value = {'follower1', 'follower2'}
        mock_following.return_value = {'following1', 'following2'}
        mock_posts.return_value = [{'shortcode': 'ABC123'}]
        
        result = self.collector.collect_user_data('test_user')
        
        # 결과 구조 검증
        assert 'profile' in result
        assert 'followers' in result
        assert 'following' in result
        assert 'posts' in result
        
        assert result['profile']['username'] == 'test_user'
        assert len(result['followers']) == 2
        assert len(result['following']) == 2
        assert len(result['posts']) == 1
        
        # 모든 메소드가 호출되었는지 확인
        mock_profile.assert_called_once_with('test_user')
        mock_followers.assert_called_once_with('test_user')
        mock_following.assert_called_once_with('test_user')
        mock_posts.assert_called_once_with('test_user')
    
    def test_save_data(self, tmp_path):
        """데이터 저장 테스트"""
        test_data = {
            'username': 'test_user',
            'followers': 1000
        }
        
        test_file = tmp_path / "test_data.json"
        
        self.collector.save_data(test_data, str(test_file))
        
        # 파일이 생성되었는지 확인
        assert test_file.exists()
        
        # 파일 내용 확인
        import json
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data['username'] == 'test_user'
        assert loaded_data['followers'] == 1000
    
    def test_initialization_without_login(self):
        """로그인 없이 초기화 테스트"""
        collector = InstagramDataCollector(use_login=False)
        
        assert collector.use_login is False
        assert collector.loader is not None
    
    def test_initialization_with_login(self):
        """로그인과 함께 초기화 테스트 (모킹)"""
        with patch.object(InstagramDataCollector, 'login'):
            collector = InstagramDataCollector(use_login=True)
            
            assert collector.use_login is True
    
    @patch('os.environ.get')
    def test_login_without_credentials(self, mock_env):
        """로그인 정보 없이 로그인 시도 테스트"""
        mock_env.return_value = None
        
        # 경고 로그가 출력되어야 하지만 에러는 발생하지 않아야 함
        self.collector.login()
        
        # 로그인 정보가 없으므로 아무 작업도 수행되지 않아야 함
        assert True  # 에러가 발생하지 않으면 성공


if __name__ == '__main__':
    # 개별 테스트 실행 가능
    pytest.main([__file__, '-v'])