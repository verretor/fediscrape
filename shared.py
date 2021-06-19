import json
import requests
import sys
import time

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
    json_instance, status_code = fetch(url)

    # If status_code == 404, this is probably a Misskey instance.
    if status_code == 404:
        url = f'https://{domain_name}/api/meta'
        json_instance, status_code = fetch(url, http_method='POST')
        if status_code == 200:
            return 'Misskey'
        else:
            return -1

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

def fetch(url, tries=5, http_method='GET', payload={}):
    '''
    Returns an HTTP response (requests.models.Response) and a status code (int).

            Parameters:
                    url (str): URL to fetch (GET request).
                    tries (int): How many requests before abandoning (Optional).
                    http_method (str): HTTP method GET/POST (Optional)
                    payload (dict): Request payload (Optional)

            Returns:
                    r (requests.models.Response), status_code (int): HTTP response, status code.

            In case of error:
                    Returns -1 (int), -1 (int).
    '''
    SLEEP = 5
    status_code = -1

    for i in range(tries):
        try:
            if http_method == 'GET':
                r = requests.get(url, data=json.dumps(payload))
            else:
                r = requests.post(url, data=json.dumps(payload))
            status_code = r.status_code
            if status_code == 200 or status_code == 404:
                time.sleep(SLEEP)
                return (r, status_code)
        except requests.exceptions.ConnectionError as e:
            sys.stderr.write(f'{e}\n')
        except requests.exceptions.MissingSchema as e:
            sys.stderr.write(f'{e}\n')
            return -1, -1
        except requests.exceptions.InvalidURL as e:
            sys.stderr.write(f'{e}\n')
            return -1, -1
        except UnicodeError as e:
            sys.stderr.write(f'{e}\n')
            return -1, -1
        time.sleep(SLEEP)

    sys.stderr.write(f'Connection failed after {tries} tries.\n')
    return -1, -1

def load_json(json_data):
    '''
    Returns a parsed JSON (list or dict). 

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
