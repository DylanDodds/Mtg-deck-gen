from selenium import webdriver
from data_agent import DataAgent
from selenium.webdriver.firefox.options import Options
import threading


def main():
    data_agent = DataAgent()
    events = data_agent.find_events()

    threads = []
    on = 0
    start_point = 152
    end_point = 2000
    for event in events:
        on += 1
        if on >= end_point:
            return

        if on < start_point:
            continue

        processThread = threading.Thread(target=process, args=[event, data_agent])
        processThread.start()
        threads.append(processThread)

        if len(threads) >= 8:
            for thread in threads:
                thread.join()
            threads = []
            print("{}/{}".format(str(on), len(events)))


def process(event, data_agent):
    cards = []
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options)
    try:
        url = event['event_url']
        driver.get(url)
        card_spans = driver.find_elements_by_class_name('L14')
        for card_span in card_spans:
            card = {
                "title": card_span.find_element_by_xpath('..').text,
                "events": [event['_id']]
            }
            cards.append(card)

        card_ids = []
        for card in cards:
            data = data_agent.find_cards({'title': card['title']})
            if data is not None and len(data) > 0:
                data_agent.add_event_to_existing_card(card['title'], event['_id'])
                card_ids.append(data[0]['_id'])
            else:
                card_ids.append(data_agent.push_card(card))
        data_agent.set_cards_of_existing_event(card_ids, event['_id'])

    except Exception as ex:
        print("Exception occurred in data process", str(ex))
    finally:
        driver.close()


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