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
    guild_ranks = [1, 3, 4]
    guild_alt_ranks = [0, 2, 5]

    base_api_url = 'http://eu.battle.net/api/wow'

    def __init__(self, rank_type):
        if rank_type == 'mains':
            self.type = 'mains'
            self.ranks = self.guild_ranks
        else:
            self.type = 'alts'
            self.ranks = self.guild_alt_ranks

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

        self.parsed_characters = [x for x in self.parsed_characters if x != []]

        # Order characters by iLevel.
        self.parsed_characters.sort(key=lambda x: x[4], reverse=True)

    def build_classes(self):
        api_classes = requests.get('{base_api_url}/data/character/classes'.format(
            base_api_url=self.base_api_url
        )).json()['classes']

        for cls in api_classes:
            self.classes[cls['id']] = cls['name']

    def get_characters(self):
        url = u'{base_api_url}/guild/{realm}/{guild}?fields=members'.format(
            base_api_url=self.base_api_url,
            realm=quote(self.realm),
            guild=quote(self.guild)
        )

        member_data = requests.get(url).json()

        if 'members' in member_data:
            return [
                member['character'] for member in requests.get(url).json()['members']
                if member['rank'] in self.ranks
                and member['character']['level'] == 100
            ]
        else:
            return []

    def get_character(self, character):
        md5 = hashlib.md5()
        md5.update(character['name'].encode('utf8'))
        pickle_file = u'pickles/{}.txt'.format(md5.hexdigest())

        url = u'{base_api_url}/character/{realm}/{name}?fields=items,professions,talents'.format(
            base_api_url=self.base_api_url,
            realm=quote(character['realm']),
            name=character['name']
        )

        data = requests.get(url).json()

        if 'name' not in data:
            # Try to load from the pickle.
            try:
                return pickle.load(file(pickle_file))
            except:
                pass

            print character['name'], character['realm'], data
            return []

        # Delete the pickle file.
        try:
            os.remove(pickle_file)
        except:
            pass

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

        if 'items' in data:
            items = [
                data['items'][slot]['itemLevel']
                if slot in data['items']
                else 'N/A'
                for slot in ITEM_SLOTS

            ]
        else:
            items = ['N/A' for slot in ITEM_SLOTS]

        if data['items']['averageItemLevelEquipped'] < 630:
            return []

        char_data = [
            u'=HYPERLINK("http://eu.battle.net/wow/en/character/{realm}/{name}/advanced", "{name}")'.format(**data),
            self.classes[data['class']],
            data['talents'][0]['spec']['name'],
            data['talents'][1]['spec']['name'] if 'spec' in data['talents'][1] else '',
            data['items']['averageItemLevelEquipped'],
            data['items']['averageItemLevel'],
            data['professions']['primary'][0]['name'] if len(data['professions']['primary']) > 0 else '',
            data['professions']['primary'][0]['rank'] if len(data['professions']['primary']) > 0 else '',
            data['professions']['primary'][1]['name'] if len(data['professions']['primary']) > 1 else '',
            data['professions']['primary'][1]['rank'] if len(data['professions']['primary']) > 1 else '',
        ] + items

        pickle.dump(char_data, file(pickle_file, 'w'))

        return char_data

    def save_csv(self):
        try:
            os.remove('output-{}.csv'.format(
                self.type
            ))
        except:
            pass

        with open('output-{}.csv'.format(self.type), 'wb') as f:
            w = unicodecsv.writer(f, encoding='utf-8')
            for row in self.parsed_characters:
                w.writerow(row)

    def return_csv(self):
        # print 'Writing CSV'
        f = StringIO()
        w = unicodecsv.writer(f, encoding='utf-8')

        for row in self.parsed_characters:
            w.writerow(row)

        f.seek(0)
        return f

if __name__ == '__main__':
    mains = Runner('mains')
    mains.save_csv()

    alts = Runner('alts')
    alts.save_csv()
