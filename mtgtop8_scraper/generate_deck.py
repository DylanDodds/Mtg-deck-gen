from data_agent import DataAgent
from random import randint

def main():
    data_agent = DataAgent()
    print("Fetching scored cards...")
    cards = data_agent.find_scored_cards({'points': {'$gt': 0}})
    print("Fetching scored pairs...")
    pairs = data_agent.find_scored_pairs({'score': {'$gt': 0}})
    print("Running genetic algorithm")
    best_deck = genetic_algorithm(cards, pairs)
    print("DONE!")
    for card_entry in best_deck:
        print("{} ... {}".format(cards[card_entry['card']]['title'], str(card_entry['score'])))


def generate_deck(cards):
    print('Generating Deck...')
    population_size = 75
    deck = []
    skip = False
    while True:
        card_index = randint(0, len(cards)-1)
        while cards[card_index]['points'] == 0:
            card_index = randint(0, len(cards) - 1)

        for card_entry in deck:
            if cards[card_index]['title'].replace(' ', '').join([i for i in cards[card_index]['title'] if not i.isdigit()]).lower() == cards[card_entry['card']]['title'].replace(' ', '').join([i for i in cards[card_entry['card']]['title'] if not i.isdigit()]).lower():
                skip = True
                break
        if skip:
            skip = False
            continue
        else:
            deck.append({'card': card_index, 'score': cards[card_index]['points']})

        card_count = 0
        for card_entry in deck:
            card_count += int(cards[card_entry['card']]['title'][:2].replace(" ", ""))
        if card_count >= population_size:
            print("[DONE!]")
            return deck


def calculate_deck_score(cards, deck, pairs):
    print("calculating score of deck...")
    score = 0

    # Add score of cards
    for card_entry in deck:
        score += card_entry['score']

    for card_index in deck:

        for paired_card_index in deck:
            if paired_card_index['card'] == card_index['card']:
                continue

            i1 = card_index['card']
            i2 = paired_card_index['card']

            # swap values if needed
            if i1 > i2:
                i1 = paired_card_index['card']
                i2 = card_index['card']

            pair_name = str(cards[i1]['_id']) + '--' + str(cards[i2]['_id'])

            # Add score of pairs
            if pair_name in pairs:
                score += pairs[pair_name]['score']
    return score


def mutate_deck(deck, cards):
    skip = False
    score = 0
    # Generate card total score
    for card_entry in deck:
        score += card_entry['score']

    average = score / len(deck) # The average point score

    mutations = 0
    for i in range(0, len(deck)):
        if cards[deck[i]['card']]['points'] > average:
            continue

        card_index = randint(0, len(cards)-1)
        while cards[card_index]['points'] == 0:
            card_index = randint(0, len(cards) - 1)
        for card in deck:
            if card['card'] == card_index:
                skip = True
        # for card_entry in deck:
        #     try:
        #         if cards[card_index]['title'].replace(' ', '').join([i for i in cards[card_index]['title'] if not i.isdigit()]).lower() == cards[card_entry['card']]['title'].replace(' ', '').join([i for i in cards[card_entry['card']]['title'] if not i.isdigit()]).lower():
        #             skip = True
        #             break
        #     except Exception as err:
        #         continue
        if skip:
            skip = False
            continue

        new_card_score = cards[card_index]['points']
        if new_card_score > deck[i]['score']:
            deck[i] = {'card': card_index, 'score': new_card_score}
            mutations += 1

    print("{} mutations made this iteration.".format(str(mutations)))
    return deck


def genetic_algorithm(cards, pairs):
    iterations = 3000
    deck = generate_deck(cards)

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
    print("best ever: " + str(best_score))
    return best_ever



if __name__ == '__main__':
    main()