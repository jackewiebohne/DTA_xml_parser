from bs4 import BeautifulSoup
import pathlib as pl
import time, os, string
from collections import defaultdict
import regex as re
import German_spelling_and_stopwords_r as gss


def PunctuationRemover(wordsstring, normalise_spelling=False, return_list=True):
    a = wordsstring
    if normalise_spelling == True:
        a = wordsstring.replace('oͤ', 'ö').replace('Oͤ', 'Ö').replace('aͤ', 'ä').replace('Aͤ', 'Ä').replace('uͤ', 'ü').replace('Uͤ', 'Ü')\
            .replace('ſ', 's').replace('æ', 'ae').replace('ï', 'i').replace('ꝛc', 'etc').replace('Ï', 'I').replace('Æ', 'Ae').replace('/', ' ')\
            .replace('-', '').replace('̃n', 'n').replace('̃N', 'N')
    translator = str.maketrans('', '', string.punctuation)
    g = a.translate(translator)
    h = re.sub('(«|»)', '', g)
    if return_list == True:
        h = h.split()
    return h


def GermanCityDeLatiniser(wordstring):
    string = ''
    for word in wordstring.split():
        if word in gss.Latin_to_German_cities:
            string += gss.Latin_to_German_cities.get(word) + ' '
        else:
            string += word + ' '
    return string


def WordLabeler(wordlist): #make sure punctuation is removed in the wordlist, otherwise it won't return, say, a city if is followed by punctuation
    h = []
    # lang = [x for x in gss.languages[0]] #ultimately for this to work, the wordlist has to go through the suffixremover first
    coun = [x for x in gss.countries.split()]
    ita = [x for x in gss.Italian_cities.split()]
    fre = [x for x in gss.French_cities.split()]
    ger = [x for x in gss.German_cities.split()]
    aus = [x for x in gss.Austrian_cities.split()]
    reg = [x for x in gss.German_regions.split()]
    tc = gss.territorial_classifiers#[x for x in gss.territorial_classifiers]
    dia = [x for x in gss.German_dialects.split()]
    uk = [x for x in gss.UK_cities.split()]
    pol = [x for x in gss.Polish_cities.split()]
    swiss = [x for x in gss.Swiss_cities.split()]
    span = [x for x in gss.Spanish_cities.split()]
    spec = [x for x in gss.special_cases.split()]

    for index, word in enumerate((wordlist)):
        # if word in lang:
        #     h.extend(('LANGUAGE:', word))
        if word in spec:
            if wordlist[index - 8: index + 8] in tc or wordlist[index - 1] in gss.loc_prepositions \
                    or wordlist[index - 1] in gss.loc_prepositions_caps:
                h.extend(('GERMAN_CITY:', word))
        if word[:-1] in spec:
            if wordlist[index - 8: index + 8] in tc or wordlist[index - 1] in gss.loc_prepositions \
                    or wordlist[index - 1] in gss.loc_prepositions_caps:
                h.extend(('GERMAN_CITY:', word[:-1]))
        if wordlist[index - 1] not in gss.determiners and wordlist[index - 1] not in tc \
                or wordlist[index-5: index+5] in tc: #to check whether the preceding word is a determiner, which would likely indicate that it is not a city (e.g. 'Essen' == Stadt, 'das Essen'== food) or if territorial classifiers are used in the surroundings of the word
            if word in ger:
                h.extend(('GERMAN_CITY:', word))
            if word in reg:
                h.extend(('REGION_IN_GERMANY:', word))
            if word in swiss:
                h.extend(('SWISS_CITY:', word))
            if word in pol:
                h.extend(('POLISH_CITY:', word))
            if word[-1:] == 's': #word[:-1] removes the last letter of word to check whether the word is used in genitive case with added 's'
                if word[:-1] in ger:
                    h.extend(('GERMAN_CITY:', word[:-1]))
                if word[:-1] in reg:
                    h.extend(('REGION_IN_GERMANY:', word[:-1]))
                if word[:-1] in coun:
                    h.extend(('COUNTRY:', word[:-1]))
                if word[:-1] in span:
                    h.extend(('SPANISH_CITY:', word[:-1]))
                if word[:-1] in aus:
                    h.extend(('AUSTRIAN_CITY:', word[:-1]))
                if word[:-1] in fre:
                    h.extend(('FRENCH_CITY:', word[:-1]))
                if word[:-1] in ita:
                    h.extend(('ITALIAN_CITY:', word[:-1]))
                if word[:-1] in uk:
                    h.extend(('UK_CITY:', word[:-1]))
                if word[:-1] in swiss:
                    h.extend(('SWISS_CITY:', word[:-1]))
                if word[:-1] in pol:
                    h.extend(('POLISH_CITY:', word[:-1]))
            if word in span:
                h.extend(('SPANISH_CITY:', word))
            if word in aus:
                h.extend(('AUSTRIAN_CITY:', word))
            if word in fre:
                h.extend(('FRENCH_CITY:', word))
            if word in ita:
                h.extend(('ITALIAN_CITY:', word))
            if word in uk:
                h.extend(('UK_CITY:', word))
            if word in coun:
                h.extend(('COUNTRY:', word))
        if word in dia:
            h.extend(('GERMAN_DIALECT:', word))
        # if word in tc:
        #     h.extend(('TERRITORIAL CLASSIFICATION:', word))
        # elif word not in h: #comment these two lines for just the list, otherwise gives complete list, not just langs, countries etc.
        #     h.append(word) #comment these two lines for just the list, otherwise gives complete list, not just langs, countries etc.
    # return h
    l = []
    counter = 1
    for i in range(1, len(h), 2):
        if h[i] == '/':
            continue
        unique = True
        l.append(h[0 + i - 1])  # appends the classifier
        l.append(h[i])  # append the element in above-specified range (2n+1)
        counter = 1
        for j in range(i + 2, len(h), 2):  # then iterate over all the remaining (2n+1)+2 elements
            if h[i] == h[j]:
                h[j] = '/'
                unique = False
                counter += 1
        if unique == False:
            h[i] = '/'
            l.append(counter)  # to count how many times l[i] and l[j] were matched
    return l

def dta_xml_parser(path_to_files: str, csv_filename: str, csv_header=True, date=True, author=True, publisher_loc=True, text_class=True,
                   geodata=False, title=False, reference_to_ppl=False, text=False, word_count=False, flush_buffer_n_write_to_file=True):
    '''
    Make sure to download all of the DTA's files. link here:
    http://www.deutschestextarchiv.de/download

    Note that this parser parses the complete xml files,
    not the metadata files that can be donwloaded (as xml) from the DTA webpage.

    Sample input for path_to_files and filename parameters are below:
    path_to_files = 'C:/Users/python/dta_komplett_2020-01-14/'
    filename = './DTA outputs/dta_csv.txt'
    '''

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
