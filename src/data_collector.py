import instaloader
from dotenv import load_dotenv
import os

load_dotenv()

def login(username=os.environ.get("INSTA_USER"), password=os.environ.get("INSTA_PASS")):
    L = instaloader.Instaloader()
    try:
        L.load_session_from_file(username)
    except FileNotFoundError:
        L.login(username, password)
        L.save_session_to_file()
    return L

def get_profile_info(username):
    pass

def get_followers(username):
    pass

def get_posts(username):
    pass