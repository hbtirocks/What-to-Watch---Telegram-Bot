import requests, json, re
indx = 0
def movie_scrapper(search):
    search = search.lower().strip()
    config = open('config.json')
    config_json = json.load(config)
    movie_db = config_json['movie_db'][indx]
    header = config_json[movie_db]['header']
    url = config_json[movie_db]['url']
    if header.get('method', 'POST') == 'GET':
        header['path'] = header['path'].format(search)
        url = url.format(search)
    elif header.get('method', 'POST') == 'POST':
        if movie_db == 'metacritic':
            header['content-length'] = format(header['content-length'], str(43+len(search)))
            form_data = config_json[movie_db]['formdata']
            form_data['search_term'] = form_data['search_term'].format(search)
        else:
            form_data = config_json[movie_db]['formdata']
            form_data = form_data.replace("{0}", search)

    try:
        if header['method'] == 'GET':
            req = requests.get(url = url, headers = header)
        elif header['method'] == 'POST':
            req = requests.post(url = url, data = form_data, headers = header)
            
    except:
        print('Error in loading data..')
        config.close()
        calling_func(search)
        return 0
    
    if req.status_code == 200:
        res = json.loads(req.content)
        if len(res) == 0:
            print('No matching result at {0} '.format(movie_db))
            config.close()
            calling_func(search)
            return 0
        else:
            return globals()[movie_db+'_db'](search, res)
            
    else:
        print('{0} :- {1}'.format(req.status_code, 'Unidentified problem..'))
        config.close()
        calling_func(search)

def imdb_db(search, res):
    regex = "[\"\']"
    otpt = []
    search = search.split(' ')
    data = res['d']
    for i in range(len(data)):
        get_catgry = data[i].get('qid', '').lower()
        set_catgry = ''
        if get_catgry.find('movie') != -1:
            set_catgry = 'Movie'
        elif get_catgry.find('tvseries') != -1:
            set_catgry = 'Tv Series'
            
        if set_catgry != '':
            for j in range(len(search)):
                if data[i].get('l', '').lower().find(search[j]) != -1:
                    otpt.append({'name':data[i].get('l', ''), 'catgry':set_catgry, 'poster':data[i].get('i', {}).get('imageUrl', ''), 'year':data[i].get('y', '')})
                    break
    if len(otpt) == 0:
        for i in range(len(data)):
            get_catgry = data[i].get('qid', '').lower()
            set_catgry = ''
            if get_catgry.find('movie') != -1:
                set_catgry = 'Movie'
            elif get_catgry.find('tvseries') != -1:
                set_catgry = 'Tv Series'
            
            if set_catgry != '':
                otpt.append({'name':data[i].get('l', ''), 'catgry':set_catgry, 'poster':data[i].get('i', {}).get('imageUrl', ''), 'year':data[i].get('y', '')})
                if len(otpt) == 4:
                    break
    return otpt

def cinematerial_db(search, res):
    regex = "[\"\']"
    otpt = []
    search = search.split(' ')
    for i in range(len(res)):
        get_catgry = res[i].get('url', '').lower()
        set_catgry = ''
        if get_catgry.find('movies') != -1:
            set_catgry = 'Movie'
        elif get_catgry.find('tv') != -1:
            set_catgry = 'Tv Series'

        if set_catgry != '':
            for j in range(len(search)):
                if res[i].get('name', '').lower().find(search[j]) != -1:
                    otpt.append({'name':re.sub(regex, '', res[i].get('name', '')), 'catgry':set_catgry, 'poster':res[i].get('url', ''), 'year':res[i].get('year', '')})
                    break
    if len(otpt) == 0:
        for i in range(len(res)):
            get_catgry = res[i].get('url', '').lower()
            set_catgry = ''
            if get_catgry.find('movies') != -1:
                set_catgry = 'Movie'
            elif get_catgry.find('tv') != -1:
                set_catgry = 'Tv Series'

            if set_catgry != '':
                otpt.append({'name':re.sub(regex, '', res[i].get('name', '')), 'catgry':set_catgry, 'poster':res[i].get('url', ''), 'year':res[i].get('year', '')})
                if len(otpt) == 4:
                    break

    return otpt

def metacritic_db(search, res):
    otpt = []
    search = search.split(' ')
    data = res['autoComplete']['results']
    for i in range(len(data)):
        get_catgry = data[i].get('refType', '').lower()
        set_catgry = ''
        if get_catgry.find('movie') != -1:
            set_catgry = 'Movie'
        elif get_catgry.find('tv') != -1:
            set_catgry = 'Tv Series'

        if set_catgry != '':
            for j in range(len(search)):
                if data[i]['name'].lower().find(search[j]) != -1:
                    otpt.append({'name':data[i].get('name', ''), 'catgry':set_catgry, 'poster':data[i].get('imagePath', ''), 'year':data[i].get('itemDate', ''),})
                    break
    if len(otpt) == 0:
        for i in range(len(data)):
            get_catgry = data[i].get('refType', '').lower()
            set_catgry = ''
            if get_catgry.find('movie') != -1:
                set_catgry = 'Movie'
            elif get_catgry.find('tv') != -1:
                set_catgry = 'Tv Series'

            if set_catgry != '':
                otpt.append({'name':data[i].get('name', ''), 'catgry':set_catgry, 'poster':data[i].get('imagePath', ''), 'year':data[i].get('itemDate', ''),})
                if len(otpt) == 4:
                    break
    return otpt

def rottentomatoes_db(search, res):
    print(res)

def calling_func(search):
    global indx
    indx += 1
    if indx < 3:
        movie_scrapper(search)
    else:
        print('Maximum calling request size exceeded')

movie_scrapper('Dil')
    
