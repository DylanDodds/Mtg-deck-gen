from data_agent import DataAgent
import threading
from random import randint
import time

def main():
    data_agent = DataAgent()
    print("scoring cards")
    # start = 4000
    # end = 4881
    # threads = []
    # max_threads = 8
    # diff = end - start
    # per_thread = int(diff/max_threads)
    # for i in range(0, max_threads):
    #     processThread = threading.Thread(target=get_and_point_cards, args=[start, end])
    #     processThread.start()
    #     threads.append(processThread)
    #     end += per_thread
    #     start += per_thread
    #
    # for thread in threads:
    #     thread.join()

    #cards = get_and_point_cards()
    cards = data_agent.find_cards()
    print("generating pairs")
    generate_pairs(cards)
    print("scoring pairs")
    start = 0
    #pairs = get_and_point_pair(data_agent, start, end)
    print("Running genetic algorithm")
    best_deck = genetic_algorithm(data_agent, cards, pairs)
    print("DONE!")
    #for card_entry in best_deck:
        #print("{} ... {}".format(cards[card_entry['card']]['title'], card_entry['score']))


def get_and_map_events(data_agent):
    print("fetching events")
    events = data_agent.find_events()
    event_out = {}
    for event in events:
        event_out[event['_id']] = event
    print("events fetched")
    return event_out

def generate_pairs(cards):
    start = 0
    end = 1000
    threads = []
    max_threads = 8
    diff = end - start
    per_thread = int(diff/8)

    end = per_thread
    mapped_events = get_and_map_events(DataAgent())
    for i in range(0, max_threads):
        processThread = threading.Thread(target=pair_process, args=[cards, start, end, mapped_events])
        processThread.start()
        threads.append(processThread)
        start += per_thread
        end += per_thread

    for thread in threads:
        thread.join()
    print("Done generating pairs!")


def pair_process(cards, start, end, mapped_events):
    data_agent = DataAgent()
    pairs = []
    pair_names = []
    on = start

    for i in range(start, end):
        on += 1
        card = cards[i]
        # iterate through every card after our current one
        for j in range(on+1, len(cards)):
            if cards[j]['_id'] == card['_id']:
                continue
            common_events = []
            for event in card['events']:
                if event in cards[j]['events']:
                    common_events.append(event)
            if len(common_events) > 0:
                pair_name = str(card['_id']) + '--' + str(cards[j]['_id'])
                if pair_name in pair_names:
                    continue
                card_pair = {'pair': pair_name, 'events': common_events,
                             'cards': [card['_id'], cards[j]['_id']]}
                card_pair['score'] = calculate_score_of_raw_pair(card_pair, mapped_events)
                pairs.append(card_pair)
                pair_names.append(card_pair)
            if len(pairs) > 10:
                data_agent.push_card_scored_pairs(pairs)
                pairs = []
        print("{}/{} cards for pairs".format(str(on), end))
    data_agent.push_card_scored_pairs(pairs)
    print("done pairing")


def get_and_point_cards(start, end):
    data_agent = DataAgent()
    cards = data_agent.find_cards()
    cards_out = []
    count = 0
    for card in cards:
        count += 1
        if count <= start:
            continue
        if count >= end:
            break
        card['points'] = calculate_score_of_card(card, data_agent)
        cards_out.append(card)
        if count % 10 == 0:
            print("card scoring: {}/{}".format(str(count), str(len(cards))))
            data_agent.push_scored_cards(cards_out)
            cards_out = []
    data_agent.push_scored_cards(cards_out)
    return cards_out


def calculate_score_of_raw_pair(pair, mapped_events):
    event_ids = pair['events']
    score = 0
    try:
        for event_id in event_ids:
            event = mapped_events[event_id]
            score += convert_rank_to_score(event['rank'])
        return score
    except Exception as ex:
        print(ex)
        return score


def calculate_score_of_card(card, data_agent):
    score = 0
    for event_id in card['events']:
        events = data_agent.find_events({'_id': event_id})
        if events is not None and len(events) > 0:
            score += convert_rank_to_score(events[0]['rank'])
    return score


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
    return 0


def generate_deck(data_agent, cards):
    print('generating deck')
    population_size = 75
    deck = []
    skip = False
    while True:
        card_index = randint(0, len(cards))

        for card_entry in deck:
            if card_index == card_entry['card']:
                skip = True
                break
            in_deck_title = cards[card_entry['card']]['title']
            in_formated = in_deck_title.join([i for i in in_deck_title if not i.isdigit()]).replace(" ", "")
            request_title = cards[card_index]['title']
            request_formatted = request_title.join([i for i in request_title if not i.isdigit()]).replace(" ", "")

            if in_formated.lower() == request_formatted.lower():
                skip = True
                break
        if skip:
            skip = False
            continue
        deck.append({'card': card_index, 'score': cards[card_index]['score']})

        if len(deck) >= population_size:
            return deck


def calculate_deck_score(cards, deck, pairs):
    print("calculating score of deck...")
    score = 0
    for card_entry in deck:
        score += card_entry['score']

    index = 0
    for card_index in deck:
        active = 0
        for paired_card_index in deck:
            if active == index:
                continue

            i1 = card_index
            i2 = paired_card_index
            # swap values if needed
            if i1 > i2:
                i1 = paired_card_index
                i2 = card_index
            pair_name = cards[i1]['title'] + '--' + cards[i2]['title']
            if pair_name in pairs:
                score += pairs[pair_name]['score']
            active += 1
        index += 1
    return score


def mutate_deck(deck, cards):
    skip = False
    score = 0
    for card_entry in deck:
        score += cards[card_entry['card']]['score']
    average = score / len(deck)
    mutations = 0
    for i in range(0, len(deck)):
        if cards[deck[i]['card']]['score'] > average:
            continue

        card_index = randint(0, len(cards))

        for card_entry in deck:
            if card_index == card_entry['card']:
                skip = True
                break

            in_deck_title = cards[card_entry['card']]['title']
            in_formated = in_deck_title.join([i for i in in_deck_title if not i.isdigit()]).replace(" ", "")
            request_title = cards[card_index]['title']
            request_formatted = request_title.join([i for i in request_title if not i.isdigit()]).replace(" ", "")

            if in_formated.lower() == request_formatted.lower():
                skip = True
                break
        if skip:
            skip = False
            continue

        new_card_score = cards[card_index]['score']
        if new_card_score > deck[i]['score']:
            deck[i] = {'card': card_index, 'score': new_card_score}
            mutations += 1
    print("{} mutations made this iteration.".format(str(mutations)))
    return deck


def genetic_algorithm(data_agent, cards, pairs):
    iterations = 30000
    deck = generate_deck(data_agent, cards)
    best_ever = None
    best_score = 0

    for i in range(0, iterations):
        print("iterations: {}".format(str(i)))
        score = calculate_deck_score(cards, deck, pairs)
        if score > best_score:
            best_ever = deck
            best_score = score
        # mutate deck
        deck = mutate_deck(deck, cards)
    print("best ever" + best_score)
    return best_ever



if __name__ == '__main__':
    main()