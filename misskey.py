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
    url = f'https://{domain_name}/api/users/show'

    json_user, status_code = shared.fetch(url, http_method='POST', payload={'username': username})
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

def scrape(domain_name, payload):
    '''
    Returns list of posts (list) and post id for the next posts to fetch (str) as a tuple.

            Parameters:
                    domain_name (str): domain name.
                    payload (dict): Request payload

            Returns:
                    lst_out (list), untilId (str): List of posts and id of the last post.

            In case of error:
                    Returns -1, -1 (integers).
    '''
    url = f'https://{domain_name}/api/users/notes'
    lst_posts = []
    lst_out = []
    untilId = ''

    json_posts, status_code = shared.fetch(url, http_method='POST', payload=payload)
    if json_posts == -1:
        return -1, -1
    json_posts = json_posts.text
    lst_posts = shared.load_json(json_posts)
    if not isinstance(lst_posts, list):
        sys.stderr.write('Broken list of posts.\n')
        return -1, -1

    if not lst_posts:
        url = ''
        return lst_posts, untilId

    for post in lst_posts:
        if isinstance(post, dict):
            dict_post = {}
            if 'createdAt' in post.keys():
                dict_post['datetime'] = post['createdAt']
            if 'text' in post.keys():
                dict_post['content'] = post['text']
            if 'id' in post.keys():
                dict_post['url'] = f'https://{domain_name}/notes/{post["id"]}'

            lst_out.append(dict_post)

    # Use the id of the last post to keep fetching older posts.
    last_post = lst_posts[-1]
    if 'id' in last_post.keys():
        untilId = last_post['id']

    return lst_out, untilId
