# Functions i'm saving for reference but am no longer using

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

    end = start + per_thread
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