import requests
from bs4 import BeautifulSoup
import re
import time
import json

def movie_overview(search):
    #...............Code for generating search url from input.............
    search = search.strip().replace(' ', '+')
    url = 'https://www.google.com/search?q=' + search + '&oq=' + search
    header = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Mobile Safari/537.36',
               'connection' : 'keep-alive'}

    
    #..............Code for fetching Title.................................
    req = requests.get(url = url, headers = header)
    soup = BeautifulSoup(req.content, 'html5lib')
    movie = {}
    title = ''

    class_list = ['ssJ7i', 'B5dxMb']

    div = None

    for cls in class_list:
        div = soup.find('div', class_ = cls)
        if div != None:
            break

    if div != None:
            movie['Title'] = div.text + ' 🎬 '
            title = div.text

    #..............Code for fetching Year - Genre - Duration/ Seasons.............................
      
    div = soup.find('div', class_ = 'iAIpCb')

    if div != None:
            lst = div.find_all('span')
            movie['ygd'] = lst[len(lst)-1].text+'\n'
            #ygd- Year Genre Duration

    #..............Code for fetching type of show [i.e. Movie or Web Show]........................
    catgry = ''
    nos = 0

    if movie.get('ygd') != None:
            if movie['ygd'].find('season') > 0:
                    catgry = movie['ygd'].split(' ‧ ')
                    nos = int(catgry[len(catgry)-1].split(' ')[0])
                    catgry = 'Web Show'
            else:
                    catgry = 'Movie'
                    
    #..............Code for fetching ratings......................................................
    rating_sign = {'IMDb':'🏅', 'Rotten Tomatoes':'🍅', 'Metacritic':'🏆', 'Google users':'👍', 'defalt':'🎖'}
    class_list = ['zr7Aae', 'uR5eBd']
    ratings = ''

    for cls in class_list:
        div = soup.find('div', class_ = cls)
        if div != None:
            break

    if div != None:
            rating_typ = div.find_all('span', class_ = 'rhsB pVA7K')
            rating_val = div.find_all('span', class_ = 'gsrt KMdzJ')
            
            for i in range(len(rating_typ)):
                    if rating_sign.get(rating_typ[i].text) != None:
                            ratings += '{0} : {1} {2}\n'.format(rating_typ[i].text, rating_val[i].text, rating_sign[rating_typ[i].text])
                    else:
                            ratings += '{0} : {1} {2}\n'.format(rating_typ[i].text, rating_val[i].text, rating_sign['defalt'])

    div = soup.find('div', class_ = 'OZ8wsd')
    if div != None:
            ky = div.text
            div = soup.find('div', class_ = 'a19vA')
            if div != None:
                    val = div.span.text.split(' ')[0]
                    ratings += '{0} : {1} {2}\n'.format(ky, val, rating_sign[ky])
    movie['ratings'] = ratings

    #..............Code for fetching overview of the show.........................................               
    div = soup.find('div', class_ = 'kno-rdesc')

    if div != None:
            movie['Overview'] = div.span.text

    #..............Code for fetching Release Date - Director...................................... 
    div = soup.find_all('div', class_ = 'rVusze')

    if len(div) > 0:
            for i in range(len(div)):
                    for txt in ['elease', 'irector', 'tarring']:
                            if div[i].find('span', class_ = 'w8qArf').get_text().find(txt) > -1:
                                    movie[div[i].find('span', class_ = 'w8qArf').get_text()] = div[i].find('span', class_ = 'LrzXr kno-fv').get_text()
    for script in soup('script'):
        script.decompose()
    print(soup)
    return movie


    #...............Season Details...............
    if catgry == 'Web Show':
        for i in range(1, nos+1):
            time.sleep(1)
            search = title.strip().replace(' ', '+')+'+season+'+str(i)
            url = 'https://www.google.com/search?q=' + search + '&oq=' + search
            
            req = requests.get(url = url, headers = headers)
            
            soup = BeautifulSoup(req.content, 'html5lib')
            
            season = {}
            
            episodes = soup.find_all('div', class_ = 'pTXA9c')
            
            description = soup.find_all('div', class_ = 'Dgm9s')
            
            le = len(episodes)
            ld = len(description)
            
            if le > 0:
                args = []
                if episodes[0].get_text().find('E01') > -1:
                    args = [0, ld, 1]
                else:
                    if le > ld:
                        div = soup.find_all('div', class_ = 'zoFLnf')
                        for j in range(le-ld):
                            tag = soup.new_tag('div')
                            tag['class'] = 'Dgm9s'
                            div[j].append(tag)
                            
                    description = soup.find_all('div', class_ = 'Dgm9s')
                    ld = len(description)
                    
                    args = [ld-1, -1, -1]
                     
                for j in range(args[0], args[1], args[2]):
                    season[episodes[j].get_text().strip()] = description[j].text
                            
            reslt = '\n'
            
            for ky in season.keys():
                reslt += ky + '\n' + season[ky] + '\n\n'
                
            print(reslt)



