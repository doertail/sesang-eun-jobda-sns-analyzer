import instaloader
from dotenv import load_dotenv
import os
import json
import time
from typing import Dict, List, Set, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class InstagramDataCollector:
    def __init__(self, use_login=False):
        """
        Instagram 데이터 수집기 초기화
        
        Args:
            use_login (bool): 로그인 사용 여부 (공개 데이터만 수집할 경우 False)
        """
        self.loader = instaloader.Instaloader()
        self.use_login = use_login
        
        if use_login:
            self.login()
    
    def login(self, username=None, password=None):
        """Instagram 로그인 (선택사항 - 공개 데이터 수집 시 불필요)"""
        username = username or os.environ.get("INSTA_USER")
        password = password or os.environ.get("INSTA_PASS")
        
        if not username or not password:
            logger.warning("로그인 정보가 없습니다. 공개 데이터만 수집합니다.")
            return
            
        try:
            self.loader.load_session_from_file(username)
            logger.info(f"세션 파일에서 {username} 로그인 정보를 로드했습니다.")
        except FileNotFoundError:
            try:
                self.loader.login(username, password)
                self.loader.save_session_to_file()
                logger.info(f"{username}으로 로그인했습니다.")
            except Exception as e:
                logger.error(f"로그인 실패: {e}")
                raise
    
    def get_profile_info(self, username: str) -> Dict:
        """
        사용자 프로필 정보 수집
        
        Args:
            username (str): 인스타그램 사용자명
            
        Returns:
            Dict: 프로필 정보
        """
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            profile_info = {
                'username': profile.username,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'followers': profile.followers,
                'followees': profile.followees,
                'posts_count': profile.mediacount,
                'is_private': profile.is_private,
                'is_verified': profile.is_verified,
                'external_url': profile.external_url,
                'profile_pic_url': profile.profile_pic_url,
                'business_account': profile.is_business_account,
                'category': profile.business_category_name if profile.is_business_account else None
            }
            
            logger.info(f"{username} 프로필 정보를 수집했습니다.")
            return profile_info
            
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"사용자 {username}을 찾을 수 없습니다.")
            return {}
        except Exception as e:
            logger.error(f"{username} 프로필 정보 수집 실패: {e}")
            return {}
    
    def get_followers_list(self, username: str, limit: int = 100) -> Set[str]:
        """
        팔로워 목록 수집 (공개 계정만)
        
        Args:
            username (str): 인스타그램 사용자명
            limit (int): 수집할 최대 팔로워 수
            
        Returns:
            Set[str]: 팔로워 사용자명 목록
        """
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            if profile.is_private:
                logger.warning(f"{username}은 비공개 계정입니다.")
                return set()
            
            followers = set()
            count = 0
            
            for follower in profile.get_followers():
                if count >= limit:
                    break
                followers.add(follower.username)
                count += 1
                time.sleep(0.1)  # Rate limiting
            
            logger.info(f"{username}의 팔로워 {len(followers)}명을 수집했습니다.")
            return followers
            
        except Exception as e:
            logger.error(f"{username} 팔로워 수집 실패: {e}")
            return set()
    
    def get_following_list(self, username: str, limit: int = 100) -> Set[str]:
        """
        팔로잉 목록 수집 (공개 계정만)
        
        Args:
            username (str): 인스타그램 사용자명  
            limit (int): 수집할 최대 팔로잉 수
            
        Returns:
            Set[str]: 팔로잉 사용자명 목록
        """
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            if profile.is_private:
                logger.warning(f"{username}은 비공개 계정입니다.")
                return set()
            
            following = set()
            count = 0
            
            for followee in profile.get_followees():
                if count >= limit:
                    break
                following.add(followee.username)
                count += 1
                time.sleep(0.1)  # Rate limiting
            
            logger.info(f"{username}의 팔로잉 {len(following)}명을 수집했습니다.")
            return following
            
        except Exception as e:
            logger.error(f"{username} 팔로잉 수집 실패: {e}")
            return set()
    
    def get_recent_posts(self, username: str, limit: int = 12) -> List[Dict]:
        """
        최근 게시물 정보 수집
        
        Args:
            username (str): 인스타그램 사용자명
            limit (int): 수집할 최대 게시물 수
            
        Returns:
            List[Dict]: 게시물 정보 목록
        """
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            if profile.is_private:
                logger.warning(f"{username}은 비공개 계정입니다.")
                return []
            
            posts = []
            count = 0
            
            for post in profile.get_posts():
                if count >= limit:
                    break
                
                post_info = {
                    'shortcode': post.shortcode,
                    'caption': post.caption,
                    'likes': post.likes,
                    'comments': post.comments,
                    'date': post.date_utc.isoformat(),
                    'is_video': post.is_video,
                    'hashtags': list(post.caption_hashtags) if post.caption_hashtags else [],
                    'mentions': list(post.caption_mentions) if post.caption_mentions else [],
                    'location': post.location.name if post.location else None
                }
                
                posts.append(post_info)
                count += 1
                time.sleep(0.5)  # Rate limiting
            
            logger.info(f"{username}의 게시물 {len(posts)}개를 수집했습니다.")
            return posts
            
        except Exception as e:
            logger.error(f"{username} 게시물 수집 실패: {e}")
            return []
    
    def collect_user_data(self, username: str, include_posts: bool = True) -> Dict:
        """
        사용자의 모든 공개 데이터 수집
        
        Args:
            username (str): 인스타그램 사용자명
            include_posts (bool): 게시물 포함 여부
            
        Returns:
            Dict: 수집된 모든 데이터
        """
        logger.info(f"{username}의 데이터 수집을 시작합니다.")
        
        user_data = {
            'profile': self.get_profile_info(username),
            'followers': self.get_followers_list(username),
            'following': self.get_following_list(username),
            'posts': self.get_recent_posts(username) if include_posts else []
        }
        
        # 수집된 데이터 요약
        if user_data['profile']:
            logger.info(f"""
            {username} 데이터 수집 완료:
            - 팔로워: {len(user_data['followers'])}명
            - 팔로잉: {len(user_data['following'])}명  
            - 게시물: {len(user_data['posts'])}개
            """)
        
        return user_data
    
    def save_data(self, data: Dict, filename: str) -> None:
        """수집된 데이터를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"데이터를 {filename}에 저장했습니다.")
        except Exception as e:
            logger.error(f"데이터 저장 실패: {e}")


# 편의 함수들
def collect_instagram_data(username: str, use_login: bool = False) -> Dict:
    """간단한 데이터 수집 함수"""
    collector = InstagramDataCollector(use_login=use_login)
    return collector.collect_user_data(username)