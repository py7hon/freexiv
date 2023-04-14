#!/usr/bin/env python3

import urllib.parse

import bottle

import api
import config

def render_header():
    return '<form action="/search"><input name="q"><input type="submit" value="search"></form>'

def render_illusts(illusts):
    html = ''
    for illust in illusts:
        try:
            url = urllib.parse.urlsplit(illust['url'])
            html += f"<a href='/en/artworks/{illust['id']}'><img src='/{url.netloc}{url.path}'></a>"
        except KeyError:
            pass
    return html

@bottle.get('/')
def landing():
    html = render_header()
    landing_page = api.fetch_landing_page().json()
    html += render_illusts(landing_page['body']['thumbnails']['illust'])
    return html

@bottle.get('/en/artworks/<illust_id:int>')
def artworks(illust_id):
    html = render_header()
    pages = api.fetch_illust_pages(illust_id).json()
    for page in pages['body']:

        regular_url = page['urls']['small']
        regular_url_split = urllib.parse.urlsplit(regular_url)

        original_url = page['urls']['original']
        original_url_split = urllib.parse.urlsplit(original_url)

        html += f'<a href="/{original_url_split.netloc}{original_url_split.path}"><img src="/{regular_url_split.netloc}{regular_url_split.path}"></a>'

    illust = api.fetch_illust(illust_id).json()['body']
    html += f"<h1>{illust['illustTitle']}</h1>"
    html += f"<p>{illust['description']}</p>"
    html += f"<a href='/en/users/{illust['userId']}'>{illust['userName']}</a>"
    html += f"<h2>Comments</h2>"

    comments = api.fetch_comments(illust_id).json()
    for comment in comments['body']['comments']:
        img = comment['img']
        img_split = urllib.parse.urlsplit(img)
        html += f"<div><a href='/en/users/{comment['userId']}'><img src='/{img_split.netloc}{img_split.path}'>{comment['userName']}</a>: {comment['comment']}</div>"

    recommends = api.fetch_illust_recommends(illust_id).json()
    html += "<h2>Recommended</h2>"
    html += render_illusts(recommends['body']['illusts'])

    return html

@bottle.get('/en/users/<user_id:int>')
def users(user_id):
    html = render_header()

#    user = api.fetch_user_top(user_id).json()
#    ogp = user['body']['extraData']['meta']['ogp']
#    banner_image = ogp['image']
#    banner_image_query = urllib.parse.urlsplit(banner_image).query
#    banner_image_id = urllib.parse.parse_qs(banner_image_query)['id'][0]
#    return f"<img src='/profile_pic/{banner_image_id}'>{ogp['title']}<p>{ogp['description']}</p>"

    user = api.fetch_user_top(user_id).json()
    ogp = user['body']['extraData']['meta']['ogp']
    illusts = user['body']['illusts']

    if len(illusts) > 0:
        for illust_id, illust in illusts.items():
            image_url = illust['profileImageUrl']
            image_split = urllib.parse.urlsplit(image_url)
            html += f"<img src='/{image_split.netloc}{image_split.path}'>"
            break

    html += f"{ogp['title']}<p>{ogp['description']}</p>"

    if len(illusts) > 0:
        for illust_id, illust in illusts.items():
            url = illust['url']
            url_split = urllib.parse.urlsplit(url)
            html += f"<a href='/en/artworks/{illust_id}'><img src='/{url_split.netloc}{url_split.path}'</a>"
    return html

@bottle.get('/user_banner/<user_id:int>')
def user_banner(user_id):
    resp = api.fetch_user_banner(user_id)
    bottle.response.set_header('content-type', resp.headers.get('content-type'))
    return resp.content

@bottle.get('/search')
def search():
    html = render_header()
    search_term = bottle.request.query.q
    search_term_encoded = urllib.parse.quote(search_term)
    search_results = api.fetch_search_results(search_term).json()
    illusts = search_results['body']['illustManga']['data']
    html += render_illusts(illusts)
    return html

bottle.run(host=config.BIND_ADDRESS, server=config.SERVER, port=config.BIND_PORT)
