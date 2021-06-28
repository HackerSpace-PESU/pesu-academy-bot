import time
import requests
from instaloader import Instaloader, Profile

instagram_loader = Instaloader()

'''
def getLastPhotoDate(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["taken_at_timestamp"]


def getPhotoDescription(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]


def getLastThumbnailURL(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["thumbnail_src"]


def getPostLink(html):
    return f'https://www.instagram.com/p/{html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["shortcode"]}'


def checkVideo(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["is_video"]


def getVideoURL(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["video_url"]


def getInstagramHTML(INSTAGRAM_USERNAME):
    headers = {
        "Host": "www.instagram.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    html = requests.get("https://www.instagram.com/" +
                        INSTAGRAM_USERNAME + "/feed/?__a=1", headers=headers)
    return html
'''


def getInstagramPostContent(post):
    post_content = dict()
    post_content["username"] = post._owner_profile.username
    post_content["is-video"] = post.is_video
    post_content["caption"] = post.caption
    post_content["date"] = post.date
    post_content["date-local"] = post.date_local
    post_content["img-url"] = post.url
    post_content["video-url"] = post.video_url
    post_content["post-url"] = f"https://www.instagram.com/p/{post.shortcode}/"
    return post_content


async def getLatestInstagramPost(instagram_usernames):
    result = list()
    for username in instagram_usernames:
        print(f"Fetching instagram posts for {username}...")
        try:
            profile = Profile.from_username(instagram_loader.context, username)
            all_posts = list(profile.get_posts())
            if all_posts:
                post = all_posts[0]
            else:
                print(f"No posts found for {username}")
                continue
            post_content = getInstagramPostContent(post)
            result.append(post_content)
        except Exception as error:
            print(f"Error fetching posts from {username}: {error}")
        time.sleep(0.5)
    return result


async def getUsernameInstagramPosts(username, n=5):
    result = list()
    try:
        profile = Profile.from_username(instagram_loader.context, username)
        if not profile.is_private or profile.followed_by_viewer:
            print(f"Fetching instagram posts for {username}...")
            all_posts = profile.get_posts()
            for ctr, post in enumerate(all_posts):
                post_content = getInstagramPostContent(post)
                result.append(post_content)
                if (ctr + 1) == n:
                    break
    except Exception as error:
        print(f"Error fetching posts from {username}: {error}")
    return result
