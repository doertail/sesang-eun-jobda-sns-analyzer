import instaloader
import os
import pytest
from src.data_collector import InstagramDataCollector
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.skipif(not os.environ.get("INSTA_USER") or not os.environ.get("INSTA_PASS"), reason="Instagram credentials not provided")
def test_instaloader_login():
    collector = InstagramDataCollector(use_login=True)
    # 실제 Instagram 프로필 테스트 (공개 계정)
    profile_info = collector.get_profile_info("instagram")
    assert profile_info.get('followers', 0) >= 0

def test_get_instagram_profile():
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, "instagram")
    print(f"Followers: {profile.followers}")
    print(f"Followees: {profile.followees}")
    assert profile.followers >= 0
    assert profile.followees >= 0