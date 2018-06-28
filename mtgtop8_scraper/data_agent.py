from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from config import config

class DataAgent:
    def __init__(self):
        try:
            self.connection_string = "mongodb://{}:{}@{}:{}".format(config['mongo']['username'], config['mongo']['password'], config['mongo']['hostname'], config['mongo']['port'])
            self.client = MongoClient(self.connection_string)
            self.database = self.client[config['mongo']['database']]
        except Exception as err:
            print('[DataAgent] Failed to connect to MongoDb... ', str(err))


    def push_event(self, event):
        try:
            if self.find_events({'event_url': event['event_url']}):
                return None
            events = self.database.events
            result = events.insert_one(event)
            return result.inserted_id
        except Exception as err:
            print('[DataAgent] Failed to push event... ', str(err))
            return None


    def push_card(self, card):
        try:
            cards = self.database.cards
            result = cards.insert_one(card)
            return result.inserted_id
        except Exception as err:
            print('[DataAgent] Failed to push card... ', str(err))
            return None


    def push_scored_cards(self, card_collection):
        try:
            cards = self.database.scored_cards
            result = cards.insert_many(card_collection)
            return result.inserted_ids
        except Exception as err:
            print('[DataAgent] Failed to push scored card... ', str(err))
            return None


    def push_card_pair(self, pair):
        try:
            pairs = self.database.pairs
            result = pairs.insert_one(pair)
            return result.inserted_id
        except Exception as err:
            print('[DataAgent] Failed to push pair... ', str(err))
            return None


    def push_card_scored_pairs(self, pair_collection):
        try:
            pairs = self.database.scored_pairs
            result = pairs.insert_many(pair_collection)
            return result.inserted_ids
        except Exception as err:
            print('[DataAgent] Failed to push scored pair... ', str(err))
            return None
# UPDATE DATA

    def add_event_to_existing_card(self, card_title, event_id):
        try:
            self.database.cards.update_one({'title': card_title, 'events': {'$nin': [event_id]}},
                                           {'$push': {'events': event_id}})
        except Exception as err:
            print('[DataAgent] Failed to update card... ', str(err))
            return False


    def set_cards_of_existing_event(self, cards, event_id):
        try:
            self.database.events.update_one({'_id': event_id}, {'$set': {'cards': cards}})
        except Exception as err:
            print('[DataAgent] Failed to update event... ', str(err))
            return False


    def clear_cards_from_events(self, query={}):
        try:
            self.database.events.update_many(query,{'$set': {'cards': []}})
        except Exception as err:
            print('[DataAgent] Failed to update event... ', str(err))
            return False

# SELECT METHODS

    def find_scored_cards(self, query={}):
        try:
            scored_cards = self.database.scored_cards
            data = scored_cards.find(query)
            results = []
            for card in data:
                results.append(card)
            return results
        except Exception as err:
            print("[DataAgent] Could not find scored cards with query: {}".format(str(query)), str(err))
            return None


    def find_scored_pairs(self, query={}):
        try:
            scored_pairs = self.database.scored_pairs
            data = scored_pairs.find(query)
            results = {}
            for card in data:
                results[card['pair']] = card
            return results
        except Exception as err:
            print("[DataAgent] Could not find scored pairs with query: {}".format(str(query)), str(err))
            return None


    def find_events(self, query={}):
        try:
            events = self.database.events
            data = events.find(query)
            results = []
            for comment in data:
                results.append(comment)
            return results
        except Exception as err:
            print("[DataAgent] Could not find event with query: {}".format(str(query)), str(err))
            return None


    def find_cards(self, query={}):
        try:
            cards = self.database.cards
            data = cards.find(query)
            results = []
            for comment in data:
                results.append(comment)
            return results
        except Exception as err:
            print("[DataAgent] Could not find cards with the query: {}".format(str(query)), str(err))
            return None


    def find_card_pairs(self, query={}):
        try:
            pairs = self.database.pairs
            data = pairs.find(query)
            results = []
            for comment in data:
                results.append(comment)
            return results
        except Exception as err:
            print("[DataAgent] Could not find cards with the query: {}".format(str(query)), str(err))
            return None

