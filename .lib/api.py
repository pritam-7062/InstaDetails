#!/bin/env python3
import requests
import random
import json
from local import *

def get_page(username):
    """Fetch raw Instagram JSON for a user profile"""
    session = requests.session()
    session.headers = {'User-Agent': random.choice(useragent)}
    resp_js = session.get(f'https://www.instagram.com/{username}/?__a=1&__d=dis').text
    return resp_js

def extract_extra_info(resp_js):
    """Find emails, hashtags, mentions in raw profile HTML/JSON"""
    raw = find(resp_js)
    return {
        "emails": raw['email'],
        "tags": sort_list(raw['tags']),
        "mentions": sort_list(raw['mention']),
    }

def user_info(username):
    """Return profile info for a user (stateless)"""
    resp_js = get_page(username)
    js = json.loads(resp_js)["graphql"]["user"]

    profile = {
        'username': js['username'],
        'user_id': js['id'],
        'name': js['full_name'],
        'followers': js['edge_followed_by']['count'],
        'following': js['edge_follow']['count'],
        'posts_img': js['edge_owner_to_timeline_media']['count'],
        'posts_vid': js['edge_felix_video_timeline']['count'],
        'reels': js['highlight_reel_count'],
        'bio': js['biography'].replace('\n', ', '),
        'external_url': js['external_url'],
        'private': js['is_private'],
        'verified': js['is_verified'],
        'profile_img': urlshortner(js['profile_pic_url_hd']),
        'business_account': js['is_business_account'],
        'joined_recently': js['is_joined_recently'],
        'business_category': js['business_category_name'],
        'category': js['category_enum'],
        'has_guides': js['has_guides'],
    }

    # Limit to 12 posts max (like original code)
    total_uploads = min(js['edge_owner_to_timeline_media']['count'], 12)

    return {
        "profile": profile,
        "extra": extract_extra_info(resp_js),
        "total_uploads": total_uploads,
        "is_private": js['is_private'],
        "resp_js": resp_js,  # pass raw for post parsing
    }

def extract_post(resp_js, index):
    """Extract info for a single post (image/video)"""
    x = json.loads(resp_js)
    js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][index]['node']

    info = {
        'comments': js['edge_media_to_comment']['count'],
        'comments_disabled': js['comments_disabled'],
        'timestamp': js['taken_at_timestamp'],
        'likes': js['edge_liked_by']['count'],
        'location': js['location'],
    }

    try:
        info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
    except IndexError:
        pass

    media = []
    if 'edge_sidecar_to_children' in js:
        for child in js['edge_sidecar_to_children']['edges']:
            node = child['node']
            media.append({
                'typename': node['__typename'],
                'id': node['id'],
                'shortcode': node['shortcode'],
                'dimensions': str(node['dimensions']['height'] + node['dimensions']['width']),
                'image_url': node['display_url'],
                'is_video': node['is_video'],
                'accessibility': node['accessibility_caption'],
            })
    else:
        media.append({
            'typename': js['__typename'],
            'id': js['id'],
            'shortcode': js['shortcode'],
            'dimensions': str(js['dimensions']['height'] + js['dimensions']['width']),
            'image_url': js['display_url'],
            'is_video': js['is_video'],
            'accessibility': js['accessibility_caption'],
        })

    return {"info": info, "media": media}

def post_info(username):
    """Return posts info for a user"""
    user_data = user_info(username)

    if user_data["is_private"]:
        return {"error": "Cannot fetch posts for private accounts"}

    posts = []
    for i in range(user_data["total_uploads"]):
        posts.append(extract_post(user_data["resp_js"], i))

    return {"username": username, "posts": posts}
