from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from mtgtop8_scraper.system import utils
import asyncio
from pyppeteer import launch


def main():
    global decks, events
    decks = []
    events = []

    url_root = 'http://mtgtop8.com/'
    raw_html = utils.simple_get('http://mtgtop8.com/format?f=ST&meta=58') # All Standard Decks
    if raw_html:
        html = BeautifulSoup(raw_html, 'html.parser')

        # For every deck name on the list
        for a in html.select('a'):
            if 'archetype' in a['href']:
                deck = {'name': a.text, 'url': url_root + a['href']}
                decks.append(deck)
    else:
        print("Could not load main page")
        return 0

    # Iterate through every deck page
    for deck in decks:
        asyncio.get_event_loop().run_until_complete(scrape_events(deck['url']))
        print("Done scraping events")

import asyncio
from pyppeteer import launch

async def scrape_events(url):
    global events
    url_root = 'http://mtgtop8.com/'
    try:
        cur_page_index = 1
        browser = await launch({'headless': True, 'args': ['--no-sandbox']})
        page = await browser.newPage()
        await page.goto(url)
        while True:
            raw_html = await page.evaluate('''() => document.body.innerHTML''')
            html = BeautifulSoup(raw_html, 'html.parser')

            table = html.select('table')[4]

            index = 0
            trs = table.select('tr')
            for tr in trs:
                if index < 2:
                    index += 1
                    continue
                if index == len(trs) - 1:
                    break
                tds = tr.select('td')

                event = {
                    'deck': tds[1].select('a')[0].text,
                    'deck_url': tds[1].select('a')[0]['href'],
                    'player': tds[2].select('a')[0].text,
                    'player_url': tds[2].select('a')[0]['href'],
                    'event': tds[3].select('a')[0].text,
                    'event_url': url_root + tds[1].select('a')[0]['href'],
                    'rank': tds[5].text,
                    'date': tds[6].text
                }
                events.append(event)
                index += 1
            # Change page
            cur_page_index += 1
            await page.evaluate('() => {PageSubmit(' + str(cur_page_index) + ');}')

        await browser.close()
    except Exception as err:
        print(err)
        return



if __name__ == '__main__':
    main()