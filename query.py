import requests
import os, re
import configparser
import csv
import time, random

path_current_directory = os.path.dirname(__file__)
path_config_file = os.path.join(path_current_directory, 'config.ini')
config = configparser.ConfigParser()
config.read(path_config_file)
api_path = config['API']

## CORPORA TO USE
# BIG ONE: 'preloaded/rutenten11_8'
# SMALL ONE (good for testing): 'preloaded/ru_araneum_maius_ru'


USERNAME = api_path['username']
API_KEY = api_path['api_key']
base_url = 'https://api.sketchengine.eu/bonito/run.cgi'
data = {
 'corpname': 'preloaded/rutenten11_8',
 'format': 'json',
 'q': 'q[word="пример"]',
 'kwicleftctx': '-1:s',
 'kwicrightctx': '1:s',
 'pagesize': '100'
}

"""
Random text to test git.   
"""

collocation_to_change = re.compile(r'(?<=<<)[А-ЯЁа-яё\s]+(?=>>)')

def get_line(res, window_min=3, window_max=15):
    line_found = False
    out = None
    lines = res['Lines']
    if lines:
        for line in lines:
            if (
                window_min <= len(line['Left'][0]['str'].split()) <= window_max and
                window_min <= len(line['Right'][0]['str'].split()) <= window_max
            ):
                out = line['Left'][0]['str']
                out += ' <<' + line['Kwic'][0]['str'][1:] + '>>'
                out += line['Right'][0]['str']
                if out:
                    break
    if out:
        return out
    return None

def build_collocation_query(col: str):
    """
    :param: col: collocation string to turn into query acceptable format
    не надо спать --> [q=]
    """
    col = col.replace(',', '')
    col = col.split()
    out = ''
    for c in col:
        out += f'[word="{c}"]'
    return 'q' + out

def compose_error_sentences(line, row):
    error1 = re.sub(collocation_to_change, row[2], line)
    error2 = re.sub(collocation_to_change, row[3], line)
    error3 = re.sub(collocation_to_change, row[4], line)
    error4 = re.sub(collocation_to_change, row[5], line)
    return error1, error2, error3, error4

def main():
    with open(os.path.join(path_current_directory, 'collocations_good_bad.tsv'), newline='') as f:
        queries = csv.reader(f, delimiter='\t')
        next(queries, None)
        with open(os.path.join(path_current_directory, 'evaluation_dataset.txt'), 'w') as fw:
            print('The following collocations were not found on the corpus')
            for row in queries:
                collocation_query = build_collocation_query(row[0])
                data['q'] = collocation_query
                res = requests.get(base_url + '/view?corpname=%s' % data['corpname'], params=data, auth=(USERNAME, API_KEY)).json()
                time.sleep(random.randint(1, 2))
                line = get_line(res)
                if line:
                    error1, error2, error3, error4 = compose_error_sentences(line, row)
                    fw.write(f'{line}\n')
                    fw.write(f'{error1}\n')
                    fw.write(f'{error2}\n')
                    fw.write(f'{error3}\n')
                    fw.write(f'{error4}\n')
                    fw.write('-'*75)
                    fw.write('\n')
                else:
                    print(row[0])
    return True    

if __name__ == '__main__':
    main()