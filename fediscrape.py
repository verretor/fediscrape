#!/usr/bin/env python3

import sys

import mastodon
import misskey
import pleroma
import shared


if __name__ == '__main__':
    # Usage: ./fediscrape.py https://example.com/@user
    if (
        len(sys.argv) != 2 or sys.argv[1].count('@') != 1 or
        sys.argv[1][0] == '@' or sys.argv[1][-1] == '@'
    ):
        sys.stderr.write(f'Usage: {sys.argv[0]} username@domain\n')
        exit(1)
    handle = sys.argv[1]

    username, domain_name = handle.split('@')

    # Use the API to determine what the server is running.
    instance_software = shared.check_instance(domain_name)

    if instance_software == -1:
        sys.stderr.write(f'Could not find what server is running.\n')
        exit(1)

    # Mastodon
    if instance_software == 'Mastodon':
        url = f'https://{domain_name}/@{username}/with_replies'
        while url:
            lst_toot, url = mastodon.scrape(url)
            for toot in lst_toot:
                # Print toot on a single line.
                toot = str(toot).replace('\n', '')
                print(f'{toot}\n')
        exit()

    # Pleroma
    elif instance_software == 'Pleroma':
        user_id = pleroma.find_user(username, domain_name)
        url = f'https://{domain_name}/api/v1/accounts/{user_id}/statuses?with_muted=true&limit=40&exclude_reblogs=true'
        while url:
            lst_post, url = pleroma.scrape(url, domain_name, user_id)
            if lst_post == -1:
                exit(1)
            for post in lst_post:
                print(f'{post}\n')

    # Misskey
    elif instance_software == 'Misskey':
        user_id = misskey.find_user(username, domain_name)
        url = f'https://{domain_name}/api/users/notes'
        payload = {'limit': 100, 'userId': '5c79f16bc9c298003288f92f', 'includeReplies': True, 'includeMyRenotes': True, 'withFiles': False}
        while True:
            lst_post, untilId = misskey.scrape(domain_name, payload)
            if lst_post == -1 or untilId == -1:
                exit(1)
            for post in lst_post:
                print(f'{post}\n')
            if not untilId:
                exit()
            payload['untilId'] = untilId
