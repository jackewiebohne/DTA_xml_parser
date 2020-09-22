from bs4 import BeautifulSoup
import pathlib as pl
import time, os
from collections import defaultdict
import regex as re
from DTA_text_analyser import GermanCityDeLatiniser as delat, PunctuationRemover as pr, WordLabeler


def dta_xml_parser(path_to_files: str, csv_filename: str, csv_header=True, date=True, author=True, publisher_loc=True, text_class=True,
                   geodata=False, title=False, reference_to_ppl=False, text=False, word_count=False, flush_buffer_n_write_to_file=True):

    with open(csv_filename, "a", encoding='utf8', errors='ignore') as a:

        with open(csv_filename, "r", encoding='utf8', errors='ignore') as r:

###csv header###
            id = -1
            counter = -1 #for stop-n-go parsing: to continue from last parsing step
            lines = []
            for line in r:
                counter += 1
                lines.append(line.split(';')) #the csv separator is an underscore instead of a comma to avoid possible conflicts with commas in the xml and the geodata lists, which contain commas
            if csv_header:
                try:
                    if lines[0][0] == 'id':
                        pass
                except:
                    csv_head = 'id'
                    if date:
                        csv_head += ';date'
                    if author:
                        csv_head += ';author surname;author firstname'
                    if publisher_loc:
                        csv_head += ';publishing location'
                    if text_class:
                        csv_head += ';text class'
                    if geodata:
                        csv_head += ';geodata'
                    if reference_to_ppl:
                        csv_head += ';in-text references to people'
                    if title:
                        csv_head += ';title'
                    if text:
                        print(
                            'Note that the text will be saved in a separate file from the csv in your CWD as \"dta_texts.txt\".')
                    if word_count:
                        csv_head += ';word count of text'
                    csv_head += '\n'
                    a.write(csv_head)

###parser starts here###
            for xml in pl.Path(path_to_files).iterdir():
                string = ''
                if xml.is_file():
                    id += 1
                    string += str(id)
                    if counter == -1 or counter == 0 or id >= counter: #to pick up at the last point
                        with open(xml, 'r', encoding='utf8', errors='ignore') as file:
                            soup = BeautifulSoup(file, features='lxml')
                            if word_count:
                                word_counter = 0
                                doc_words = []

        ###date###
                            if date:
                                try:
                                    string += ';' + soup.find('sourcedesc').find_next('publicationstmt').find_next(
                                        'date').text
                                except:
                                    string += ';-99999'
                                    pass
                                print(string)

        ###author###
                            if author:
                                try:
                                    surname = soup.find('author').find_next('surname').text
                                    string += ';' + surname
                                except:
                                    string += ';-99999'
                                    pass
                                try:
                                    forename = soup.find('author').find_next('forename').text
                                    string += ';' + forename
                                except:
                                    string += ';-99999'
                                    pass

        ###publisher location###
                            if publisher_loc:
                                try:
                                    string += ';' + soup.find('sourcedesc').find_next('publicationstmt').find_next('pubplace').text
                                except:
                                    string += ';-99999'
                                    pass
                                print(string)

        ###text class###
                            if text_class:
                                try:
                                    x = soup.find('textclass').text.split()
                                    string += ';' + x[0]
                                except:
                                    string += ';-99999'
                                    pass
                                print(string)

        ###parse title and text for geolocations###
                            if geodata:
                                try:
                                    temp_string = soup.find('title').text
                                    new_string = pr(temp_string, normalise_spelling=True, return_list=False)
                                    norm_string = delat(new_string)
                                    x = WordLabeler(norm_string.split())
                                    string += str(x)
                                except:
                                    continue
                                try:
                                    print('parsing text for geolocations')
                                    start1 = time.time()
                                    lbs = soup.find('body').find_all_next('div')
                                    temp_string2 = ''
                                    for tag in lbs:
                                        temp_string2 += tag.text
                                    new_string2 = pr(temp_string2, normalise_spelling=True, return_list=False)
                                    duration1 = time.time()-start1
                                    print('punctuation removed. duration:', duration1)
                                    start2 = time.time()
                                    norm_string2 = delat(new_string2)
                                    duration2 = time.time() - start2
                                    print('delatinised german cities. duration:', duration2)
                                    start3 = time.time()
                                    x = WordLabeler(norm_string2.split())
                                    duration3 = time.time() - start3
                                    print('parsed text for geolocations. duration:', duration3)
                                    string += ';' + str(x)
                                except:
                                    string += ';'
                                    continue

        ###references to ppl (incl. author) themselves in the text###
                            if reference_to_ppl:
                                names = []
                                names.append(soup.find('text').find_all_next('persname'))
                                name_dict = defaultdict(int)
                                for i in range(len(names)):
                                    for tag in names[i]:
                                        x = tag.text
                                        new_x = x
                                        new_x = re.sub(r'-\n', '', new_x)
                                        new_x = re.sub(r'\n', ' ', new_x)
                                        new_x = re.sub('/', '', new_x)
                                        name_dict[new_x] += 1
                                string += ';'
                                for word in name_dict.keys():
                                    string += ';'
                                    string += word

        ###title###
                            if title or word_count:
                                try:
                                    if title:
                                        string += ';' + soup.find('title').text
                                    if word_count:
                                        doc_words.append(soup.find('title').text)
                                except:
                                    string += ';-99999'
                                    pass

        ###text###
                            if text or word_count:
                                string2 = ''
                                print('parsing the text')
                                try:
                                    lbs = soup.find('body').find_all_next('div')
                                    string2 += ''
                                    if word_count:
                                        print('counting words')
                                    for tag in lbs:
                                        string2 += tag.text
                                        if word_count:
                                            doc_words.append(tag.text)
                                    if word_count:
                                        for element in doc_words:
                                            for word in element.split():
                                                word_counter += 1
                                except:
                                    string += '-99999\n'
                                    pass
                            a.write(string)
                            if text:
                                with open('./dta_texts.txt', "a", encoding='utf8', errors='ignore') as t:
                                    string2 += '/////////////////\n\n\n\n'
                                    t.write('text id: ' + str(id) + '\n'+ string2)
                            if word_count:
                                a.write(';' + str(word_counter) + '\n')
                            if flush_buffer_n_write_to_file:
                                a.flush()  # flushing internal buffers
                                os.fsync(a.fileno())  # force-writing buffers to file


path_to_files = 'C:/Users/jackewiebohne/Documents/python tests/DTA/dta_komplett_2020-01-14/'
csv_filename = './DTA outputs/dta_csv.txt'
x = dta_xml_parser(path_to_files, csv_filename, author=True, title=True, text=False, csv_header=True,
                   date=True, publisher_loc=True, text_class=True, word_count=True, geodata=False, reference_to_ppl=True)