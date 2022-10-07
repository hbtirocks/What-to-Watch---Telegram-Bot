import requests, json
total_call = 0
def movie_scrapper(search, movie_db):
    search = search.lower().strip()
    config = open('config.json')
    config_json = json.load(config)
    header = config_json[movie_db]['header']
    url = config_json[movie_db]['url']
    global total_call
    total_call += 1
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
        calling_func(search, config['movie_db'], movie_db)
        return 0
    
    if req.status_code == 200:
        res = json.loads(req.content)
        if len(res) == 0:
            print(format('No matching result at {0} ', movie_db))
            calling_func(search, config['movie_db'], movie_db)
            return 0
        else:
            return globals()[movie_db+'_db'](search, res)
            
    else:
        print('{0} :- {1}'.format(req.status_code, 'Unidentified problem..'))
        calling_func(search, config['movie_db'], movie_db)

def cinematerial_db(search, res):
    otpt = []
    search = search.split(' ')
    for i in range(len(res)):
        catgry = res[i].get('url', '').lower()
        if catgry.find('movies') != -1 or catgry.find('tv') != -1:
            for j in range(len(search)):
                if res[i]['name'].lower().find(search[j]) != -1:
                    otpt.append({'name':res[i]['name'], 'url':res[i]['url'], 'year':res[i]['year']})
                    break
    if len(otpt) == 0:
        for i in range(len(res)):
            url = data[i]['url'].lower()
            if url.find('movies') != -1 or url.find('tv') != -1:
                otpt.append({'name':res[i]['name'], 'url':res[i]['url'], 'year':res[i]['year']})
                if len(otpt) == 4:
                    break

    return otpt


def imdb_db(search, res):
    otpt = []
    search = search.split(' ')
    data = res['d']
    for i in range(len(data)):
        catgry = data[i].get('qid', '').lower()
        if catgry.find('movie') != -1 or catgry.find('tvseries') != -1:
            for j in range(len(search)):
                if data[i]['l'].lower().find(search[j]) != -1:
                    otpt.append({'name':data[i].get('l'), 'catgry':data[i].get('qid'), 'poster':data[i].get('i').get('imageUrl'), 'year':data[i].get('y')})
                    break
    if len(otpt) == 0:
        for i in range(len(res)):
            catgry = data[i].get('qid', '').lower()
            if catgry.find('movie') != -1 or catgry.find('tvseries') != -1:
                otpt.append({'name':data[i].get('l'), 'catgry':data[i].get('qid'), 'poster':data[i].get('i').get('imageUrl'), 'year':data[i].get('y')})
                if len(otpt) == 4:
                    break
    return otpt

def rottentomatoes_db(search, res):
    print(res)

def metacritic_db(search, res):
    otpt = []
    search = search.split(' ')
    data = res['autoComplete']['results']
    for i in range(len(data)):
        catgry = data[i].get('refType', '').lower()
        if catgry.find('movie') != -1 or catgry.find('tv') != -1:
            for j in range(len(search)):
                if data[i]['name'].lower().find(search[j]) != -1:
                    otpt.append({'name':data[i].get('name'), 'catgry':data[i].get('refType'), 'poster':data[i].get('imagePath'), 'year':data[i].get('itemDate'),
                                 'Metacritic':data[i].get('metaScore')})
                    break
    if len(otpt) == 0:
        for i in range(len(res)):
            if data[i]['refType'] == 'Movie' or data[i]['refType'] == 'Tv':
                otpt.append({'name':data[i].get('l'), 'catgry':data[i].get('qid'), 'poster':data[i].get('imageUrl'), 'year':data[i].get('y')})
                if len(otpt) == 4:
                    break
    return otpt

def calling_func(search, db_list, movie_db):
    indx = db_list.index(movie_db)
    if indx != len(db_list)-1 and total_call <= 3:
        movie_scrapper(search, movie_db[indx+1])
    elif total_call <= 3:
        movie_scrapper(search, movie_db[0])
    else:
        print('Maximum calling request size exceeded')
    
