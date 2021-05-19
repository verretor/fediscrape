#!/usr/bin/env python3

import json
import requests
import sys
import time
from bs4 import BeautifulSoup

SLEEP = 5

def check_instance(domain_name):
    '''
    Returns the instance software as a string.

            Parameter:
                    domain_name (str): domain name.

            Returns:
                    instance_software (str): Server software.

            In case of error:
                    Returns -1 (int).
    '''
    url = f'https://{domain_name}/api/v1/instance'
    json_instance = fetch(url)
    if json_instance == -1:
        return -1
    json_instance = json_instance.text

    dict_instance = load_json(json_instance)
    if not isinstance(dict_instance, dict):
        sys.stderr.write('Error parsing instance JSON.\n')
        return -1

    if 'pleroma' in dict_instance.keys():
        return 'Pleroma'
    else:
        return 'Mastodon'

    sys.stderr.write('Server software not recognized.\n')
    return -1

def fetch(url):
    '''
    Returns an HTTP response (requests.models.Response).

            Parameter:
                    url (str): URL to fetch (GET request).

            Returns:
                    r (requests.models.Response): HTTP response.

            In case of error:
                    Returns -1 (int).
    '''
    status_code = -1

    while status_code != 200:
        try:
            r = requests.get(url)
            status_code = r.status_code
        except requests.exceptions.ConnectionError as e:
            sys.stderr.write(f'{e}\n')
        except requests.exceptions.MissingSchema as e:
            sys.stderr.write(f'{e}\n')
            return -1
        except requests.exceptions.InvalidURL as e:
            sys.stderr.write(f'{e}\n')
            return -1
        except UnicodeError as e:
            sys.stderr.write(f'{e}\n')
            return -1
        time.sleep(SLEEP)

    return r

def find_pleroma_user(username, domain_name):
    '''
    Returns domain name (str) and user id (str) as a tuple.

            Parameter:
                    username (str): user name.
                    domain_name (str): domain name.

            Returns:
                    user_id (str): User id.

            In case of error:
                    Returns -1 (int).
    '''
    url = f'https://{domain_name}/api/v1/accounts/{username}'

    json_user = fetch(url).text
    if json_user == -1:
        return -1
    dict_data = load_json(json_user)
    if not isinstance(dict_data, dict):
        sys.stderr.write('Error parsing JSON data.\n')
        return -1 
    
    if 'id' in dict_data:
        user_id = dict_data['id']
    else:
        sys.stderr.write('No user id.\n')
        return -1 

    return user_id

def load_json(json_data):
    '''
    Returns a parsed JSON. 

            Parameter:
                    json_data (str): JSON.

            Returns:
                    List or dictionary.

            In case of error:
                    Returns -1 (int).
    '''
    try:
        return json.loads(json_data)
    except json.decoder.JSONDecodeError:
        sys.stderr.write('json.decoder.JSONDecodeError\n')
        return -1

def mastodon_scrape(url):
    '''
    Returns list of toots (list) and URL for the next page to scrape (str) as a tuple.

            Parameter:
                    url (str): Profile URL.

            Returns:
                    lst_out (list), show_more_url (str): List of toots and next page url.

            In case of error:
                    Returns -1, -1 (integers).
    '''
    html_doc = fetch(url)
    # fetch() returns -1 in case of error.
    if html_doc == -1:
        return -1, -1
    html_doc = html_doc.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    lst_out = []

    toots = soup.find_all('div', attrs={'class': 'entry h-entry'})
    for toot in toots:
        toot_link = toot.find('a')
        e_content = toot.find('div', attrs={'class': 'e-content'})

        toot_time = toot.find('time', attrs={'class': 'time-ago'})
        if toot_time and 'datetime' in toot_time.attrs:
            toot_datetime = toot_time['datetime']
        else:
            toot_datetime = ''

        toot = []
        for elem in e_content:
            if elem != '\n':
                toot.append(elem)

        if e_content and toot_link and 'href' in toot_link.attrs:
            dict_toot = {'datetime': toot_datetime, 'content': toot, 'url': toot_link['href']}
            lst_out.append(dict_toot)

    show_more = soup.find_all('a', attrs={'class': 'load-more load-gap'})
    show_more_url = ''
    if show_more:
        show_more = show_more[-1]
        if 'href' in show_more.attrs and '?max_id=' in show_more['href']:
            show_more_url = show_more['href']

    return lst_out, show_more_url

def pleroma_scrape(url, domain_name, user_id):
    '''
    Returns list of posts (list) and URL for the next page to scrape (str) as a tuple.

            Parameters:
                    url (str): API URL.
                    domain_name (str): domain name.
                    user_id (str): User id.

            Returns:
                    lst_out (list), url (str): List of posts and next page url.

            In case of error:
                    Returns -1, -1 (integers).
    '''
    lst_posts = []
    lst_out = []

    json_posts = fetch(url)
    if json_posts == -1:
        return -1, -1
    json_posts = json_posts.text
    lst_posts = load_json(json_posts)
    if not isinstance(lst_posts, list):
        sys.stderr.write('Broken list of posts.\n')
        return -1, -1 

    if not lst_posts:
        url = ''
        return lst_posts, url

    for post in lst_posts:
        if isinstance(post, dict):
            dict_post = {}
            if 'created_at' in post.keys():
                dict_post['datetime'] = post['created_at']
            if 'content' in post.keys():
                dict_post['content'] = post['content']
            if 'url' in post.keys():
                dict_post['url'] = post['url']

            lst_out.append(dict_post)

    # Use the id of the last post to keep fetching older posts.
    last_post = lst_posts[-1]
    if 'id' in last_post.keys():
        max_id = last_post['id']

    url = f'https://{domain_name}/api/v1/accounts/{user_id}/statuses?max_id={max_id}&with_muted=true&limit=20'
    return lst_out, url

if __name__ == '__main__':
    # Usage: ./fediscrape.py https://example.com/@user
    if len(sys.argv) != 2 or '@' not in sys.argv[1]:
        sys.stderr.write(f'Usage: {sys.argv[0]} username@domain\n')
        exit(1)
    handle = sys.argv[1]

    username, domain_name = handle.split('@')

    # Use the API to determine what the server is running.
    instance_software = check_instance(domain_name)

    # Mastodon
    if instance_software == 'Mastodon':
        url = f'https://{domain_name}/@{username}/with_replies'
        while url:
            lst_toot, url = mastodon_scrape(url)
            for toot in lst_toot:
                # Print toot on a single line.
                toot = str(toot).replace('\n', '')
                print(f'{toot}\n')
        exit()
    elif instance_software == -1:
        exit(1)

    # Pleroma
    user_id = find_pleroma_user(username, domain_name)
    url = f'https://{domain_name}/api/v1/accounts/{user_id}/statuses?with_muted=true&limit=20'
    while url:
        lst_post, url = pleroma_scrape(url, domain_name, user_id)
        if lst_post == -1:
            exit(1)
        for post in lst_post:
            print(f'{post}\n')
