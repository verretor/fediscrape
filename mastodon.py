import shared
from bs4 import BeautifulSoup


def scrape(url):
    '''
    Returns list of toots (list) and URL for the next page to scrape (str) as a tuple.

            Parameter:
                    url (str): Profile URL.

            Returns:
                    lst_out (list), show_more_url (str): List of toots and next page url.

            In case of error:
                    Returns -1, -1 (integers).
    '''
    html_doc, status_code = shared.fetch(url)
    # shared.fetch() returns -1, -1 in case of error.
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
