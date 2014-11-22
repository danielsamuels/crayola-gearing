from cStringIO import StringIO
import hashlib
import os
import pickle
import requests
import unicodecsv
from urllib import quote

ITEM_QUALITY = {
    1: 'c',
    2: 'u',
    3: 'r',
    4: 'e',
    5: 'l',
    7: 'b'
}

ITEM_SLOTS = [
    'mainHand',
    'offHand',
    'head',
    'neck',
    'shoulder',
    'back',
    'chest',
    'wrist',
    'hands',
    'waist',
    'legs',
    'feet',
    'finger1',
    'finger2',
    'trinket1',
    'trinket2'
]


class Runner(object):

    # Ranks
    # 0 - Guild Master
    # 1 - Officer
    # 3 - Raider
    # 4 - Trial

    classes = {}

    characters = []
    parsed_characters = []

    realm = 'Lightbringer'
    guild = 'Crayola Inc'
    guild_ranks = [0, 1, 3, 4]

    base_api_url = 'http://eu.battle.net/api/wow'

    def __init__(self):
        # Ensure the pickle directory is present.
        try:
            os.mkdir('pickles')
        except:
            pass

        self.build_classes()

        self.parsed_characters = [
            self.get_character(character)
            for character in self.get_characters()
        ]

    def build_classes(self):
        api_classes = requests.get('http://eu.battle.net/api/wow/data/character/classes').json()['classes']

        for cls in api_classes:
            self.classes[cls['id']] = cls['name']

    def get_characters(self):
        url = u'{base_api_url}/guild/{realm}/{guild}?fields=members'.format(
            base_api_url=self.base_api_url,
            realm=quote(self.realm),
            guild=quote(self.guild)
        )

        return [
            member['character'] for member in requests.get(url).json()['members']
            if member['rank'] in self.guild_ranks
            and member['character']['level'] == 100
        ]

    def get_character(self, character):
        # print u'Processing {}'.format(character['name'])
        md5 = hashlib.md5()
        md5.update(character['name'].encode('utf8'))
        pickle_file = u'pickles/{}.txt'.format(md5.hexdigest())

        try:
            return pickle.load(file(pickle_file))
        except:
            pass

        url = u'{base_api_url}/character/{realm}/{name}?fields=items,professions,talents'.format(
            base_api_url=self.base_api_url,
            realm=quote(character['realm']),
            name=character['name']
        )

        data = requests.get(url).json()

        # Character
        # Class
        # Main Spec
        # Off Spec
        # Equipped iLevel
        # Max iLevel
        # Prof 1
        # Prof 1 Level
        # Prof 2
        # Prof 2 Level
        # Main Hand
        # Offhand Helm
        # Neck
        # Shoulders
        # Cloak
        # Chest
        # Bracers Hands
        # Waist
        # Legs
        # Boots
        # Ring 1
        # Ring 2
        # Trinket 1
        # Trinket 2

        items = [
            '{} {}'.format(
                data['items'][slot]['itemLevel'],
                ITEM_QUALITY[data['items'][slot]['quality']],
            )
            if slot in data['items']
            else 'N/A'
            for slot in ITEM_SLOTS

        ]

        char_data = [
            data['name'],
            self.classes[data['class']],
            data['talents'][0]['spec']['name'],
            data['talents'][1]['spec']['name'],
            data['items']['averageItemLevelEquipped'],
            data['items']['averageItemLevel'],
            data['professions']['primary'][0]['name'],
            data['professions']['primary'][0]['rank'],
            data['professions']['primary'][1]['name'],
            data['professions']['primary'][1]['rank']
        ] + items

        pickle.dump(char_data, file(pickle_file, 'w'))

        return char_data

    def output_csv(self):
        # print 'Writing CSV'
        f = StringIO()
        w = unicodecsv.writer(f, encoding='utf-8')

        for row in self.parsed_characters:
            w.writerow(row)

        f.seek(0)
        return f

if __name__ == '__main__':
    Runner()
