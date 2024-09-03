import instaloader # pip install instaloader
import json
import os
from src.utils.helper import getConfig, getLanguage
from src.classes.Log import Log

CONFIG = getConfig()
log = Log()

try:
    lang = CONFIG['language'].lower()
    if lang in ["tr", "en"]:
        lang = getLanguage(f"lang/{lang}.json")
    else:
        raise ValueError("")
except Exception as e:
    lang = getLanguage(f"lang/en.json")
    log.warning(lang["invalidLanguage"])

class InstagramDownloader:
    def __init__(self, username:str):
        try:
            log.debug("The '__init__' function of the 'InstagramDownloader' class has been executed.")
            self.username = username
            self.loader = instaloader.Instaloader()
        except Exception as e:
            log.error(f"Unexpected error in '__init__' function of the 'InstagramDownloader' class:\n{e}")
    
    def getProfile(self) -> instaloader.Profile:
        try:
            log.debug("The 'getProfile' function of the 'InstagramDownloader' class has been executed.")
            profile = instaloader.Profile.from_username(self.loader.context, self.username)
            return profile
        except Exception as e:
            log.error(f"Unexpected error in 'getProfile' function of the 'InstagramDownloader' class:\n{e}")
    
    def isPrivate(self, profile:instaloader.Profile) -> bool:
        try:
            log.debug("The 'isPrivate' function of the 'InstagramDownloader' class has been executed.")
            if profile.is_private:
                log.warning(f"{lang['privateAccount']}")
                return True
            else:
                log.info(f"{lang['publicAccount']}")
                return False
        except Exception as e:
            log.error(f"Unexpected error in 'isPrivate' function of the 'InstagramDownloader' class:\n{e}")
    
    def login(self, username, password):
        try:
            log.debug("The 'login' function of the 'InstagramDownloader' class has been executed.")
            self.loader.login(username, password)
        except instaloader.exceptions.LoginException as e:
            log.error(lang["loginException"])
        except Exception as e:
            log.error(f"Unexpected error in 'login' function of the 'InstagramDownloader' class:\n{e}")
    
    def downloadPosts(self, profile:instaloader.Profile, outputDirection:str, getMetadata:bool=False):
        try:
            log.debug("The 'downloadPosts' function of the 'InstagramDownloader' class has been executed.")
            if getMetadata:
                metaDataFile = os.path.join(outputDirection, "metaData.json")
                metaDataList = []

            self.loader.dirname_pattern = outputDirection

            for post in profile.get_posts():
                self.loader.download_post(post, target=self.username)
                
                if getMetadata:
                    comments = []
                    for comment in post.get_comments():
                        comments.append({
                            "user": comment.owner.username,
                            "text": comment.text,
                            "date": comment.created_at_utc.isoformat()
                        })

                    postData = {
                        "shortcode": post.shortcode,
                        "date": post.date_utc.isoformat(),
                        "caption": post.caption,
                        "likes": post.likes,
                        "comments_count": post.comments,
                        "tags": post.caption_hashtags,
                        "is_video": post.is_video,
                        "comments": comments
                    }
                    metaDataList.append(postData)

            if getMetadata:
                with open(metaDataFile, 'w', encoding='utf-8') as file:
                    json.dump(metaDataList, file, ensure_ascii=False, indent=4)
            
            log.info(f"[{outputDirection}] {lang['downloadSuccessful']}")
        except Exception as e:
            log.error(lang['downloadFailed'])
            log.error(f"Unexpected error in 'login' function of the 'InstagramDownloader' class:\n{e}")

def getUsername() -> str:
    try:
        log.debug("The 'getUsername' function has been executed.")
        while True:
            username = input(f"{lang['username']}: ")
            if username:
                break
            else:
                log.warning(lang['usernameEmpty'])
        return username
    except Exception as e:
        log.error(f"Unexpected error in 'login' function:\n{e}")

def main():
    try:
        log.debug("The 'main' function has been executed.")
        targetUsername = getUsername()
        getMetadata = True
        instagramDownloader = InstagramDownloader(targetUsername)

        profile = instagramDownloader.getProfile()
        if instagramDownloader.isPrivate(profile) or getMetadata:
            username = CONFIG["account"]["username"]
            password = CONFIG["account"]["password"]
            isLogin = instagramDownloader.login(username, password)
            if not isLogin:
                log.warning(lang["noMetadata"])
                getMetadata = False
            profile = instagramDownloader.getProfile()
        
        outputDirection = f"downloads/{targetUsername}"
        os.makedirs(outputDirection, exist_ok=True)

        instagramDownloader.downloadPosts(profile, outputDirection, getMetadata)
        input(lang['enterToExit'])
    except Exception as e:
        log.error(f"Unexpected error in 'main' function:\n{e}")

if __name__ == "__main__":
    main()