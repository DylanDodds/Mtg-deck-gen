from selenium import webdriver
from bs4 import BeautifulSoup
from mtgtop8_scraper.data import utils
from mtgtop8_scraper.data.data_agent import DataAgent
from datetime import datetime
import time
import threading


def main():
    data_agent = DataAgent()
    events = data_agent.find_events()

    threads = []

    for event in events:
        processThread = threading.Thread(target=process, args=[event, data_agent])
        processThread.start()
        threads.append(processThread)

        if len(threads) >= 16:
            for thread in threads:
                thread.join()
            threads = []

def process(event, data_agent):
    cards = []
    url = event['event_url']
    driver = webdriver.Firefox()
    driver.get(url)


    card_trs = driver.find_elements_by_class_name('G14')


    for card_tr in card_trs:
        try:
            card_tr.click()
            time.sleep(1)

            raw_html = driver.page_source
            html = BeautifulSoup(raw_html, 'html.parser')

            colors = []
            # select all images on the page and find color images
            images = driver.find_elements_by_css_selector('img')
            for image in images:
                color = getColor(image.get_attribute('src'))
                if color is not None and color not in colors:
                    colors.append(color)

            card = {
                "title": driver.find_elements_by_class_name('chosen_tr')[1].text,
                "colours": colors,
                "type": driver.find_elements_by_class_name('g12')[0].text,
                "events": [event['_id']]
            }
            cards.append(card)
        except:
            continue

    driver.close()
    for card in cards:
        data = data_agent.find_cards({'title': card['title']})
        if data is not None and len(data) > 0:
            data_agent.add_event_to_existing_card({'title': card['title']}, event['_id'])
        else:
            data_agent.push_card(card)


def getColor(image):
    if 'R.jpg' in image:
        return 'red'
    if 'B.jpg' in image:
        return 'black'
    if 'U.jpg' in image:
        return 'blue'
    if 'G.jpg' in image:
        return 'green'
    if 'W.jpg' in image:
        return 'white'
    return None


def convert_rank_to_score(rank):
    if rank == '1':
        return 100
    if rank == '2':
        return 80
    if rank == '3' or rank == '3-4' or rank == '4':
        return 60
    if rank == '5-8':
        return 40
    if rank == '9-16':
        return 20
    if rank == '':
        return 0

if __name__ == '__main__':
    main()