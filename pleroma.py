import shared

def find_user(username, domain_name):
    '''
    Returns user id (str).

            Parameters:
                    username (str): user name.
                    domain_name (str): domain name.

            Returns:
                    user_id (str): User id.

            In case of error:
                    Returns -1 (int).
    '''
    url = f'https://{domain_name}/api/v1/accounts/{username}'

    json_user, status_code = shared.fetch(url)
    json_user = json_user.text
    if json_user == -1:
        return -1
    dict_data = shared.load_json(json_user)
    if not isinstance(dict_data, dict):
        sys.stderr.write('Error parsing JSON data.\n')
        return -1 
    
    if 'id' in dict_data:
        user_id = dict_data['id']
        return user_id
    else:
        sys.stderr.write('No user id.\n')
        return -1 


def scrape(url, domain_name, user_id):
    '''
    Returns list of posts (list) and URL for the next url to scrape (str) as a tuple.

            Parameters:
                    url (str): API URL.
                    domain_name (str): domain name.
                    user_id (str): User id.

            Returns:
                    lst_out (list), url (str): List of posts and next url.

            In case of error:
                    Returns -1, -1 (integers).
    '''
    # Example URLs:
    # See the most recent posts.
    # https://{domain_name}/api/v1/accounts/{user_id}/statuses?with_muted=true&limit=40
    # {max_id}: Only posts older than this post's id will be shown.
    # https://{domain_name}/api/v1/accounts/{user_id}/statuses?max_id={max_id}&with_muted=true&limit=40

    lst_posts = []
    lst_out = []

    json_posts, status_code = shared.fetch(url)
    if json_posts == -1:
        return -1, -1
    json_posts = json_posts.text
    lst_posts = shared.load_json(json_posts)
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

    url = f'https://{domain_name}/api/v1/accounts/{user_id}/statuses?max_id={max_id}&with_muted=true&limit=40'
    return lst_out, url
