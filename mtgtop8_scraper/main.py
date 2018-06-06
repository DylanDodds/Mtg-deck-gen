from selenium import webdriver
from bs4 import BeautifulSoup
from mtgtop8_scraper import utils
from mtgtop8_scraper.data_agent import DataAgent
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import time
import threading

def main():
    print("started")
    global decks
    decks = []

    url_root = 'http://mtgtop8.com/'
    raw_html = utils.simple_get('http://mtgtop8.com/format?f=ST&meta=58') # All Standard Decks
    if raw_html:
        html = BeautifulSoup(raw_html, 'html.parser')

        for a in html.select('a'):
            if 'archetype' in a['href']:
                deck = {'name': a.text, 'url': url_root + a['href']}
                decks.append(deck)

    else:
        print("Could not load main page")
        return 0

    # multitask
    threads = []
    record = 0
    on = 0
    start_pos = 24
    print("hit deck loop")
    for deck in decks:
        on += 1
        if on < start_pos:
            continue

        processThread = threading.Thread(target=scrape_process, args=[deck])
        processThread.start()
        threads.append(processThread)

        if len(threads) >= 6:
            for thread in threads:
                thread.join()
            threads = []
            print("decks: {}/{}".format(str(on), str(len(decks))))

    print("Done scraping events")


def scrape_process(deck):
    data_agent = DataAgent()
    try:
        events = scrape_events(deck['url'])
        for event in events:
            data_agent.push_event(event)
    except:
        return



def scrape_events(url):
    url_root = 'http://mtgtop8.com/'
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options)
    driver.get(url)
    events = []

    try:
        cur_page_index = 1

        while True:
            try:
                raw_html = driver.page_source
                html = BeautifulSoup(raw_html, 'html.parser')
                table = html.select('table')[4]

                index = 0
                trs = table.select('tr')
            except:
                print("error, retrying, while True: loop")

            for tr in trs:
                if index < 2:
                    index += 1
                    continue
                if index == len(trs) - 1:
                    break
                tds = tr.select('td')

                event = {
                    'deck': tds[1].select('a')[0].text,
                    'deck_url': url_root + tds[1].select('a')[0]['href'],
                    'player': tds[2].select('a')[0].text,
                    'player_url': url_root + tds[2].select('a')[0]['href'],
                    'event': tds[3].select('a')[0].text,
                    'event_url': url_root + tds[1].select('a')[0]['href'],
                    'rank': tds[5].text,
                    'date': time.mktime(datetime.strptime(tds[6].text, "%d/%m/%y").timetuple()),
                    'cards': []
                }
                events.append(event)
                index += 1

            # Change page
            elements = driver.find_elements_by_class_name('Nav_PN')
            if cur_page_index == 1:
                if not elements or len(elements) < 1:
                    return events
                elements[0].click() # Next Button
            else:
                if not elements or len(elements) < 2:
                    return events
                elements[1].click()  # Next Button
            time.sleep(3)
            cur_page_index += 1
    except Exception as err:
        print(err)
        return events
    finally:
        driver.close()



if __name__ == '__main__':
    main()