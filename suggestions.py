import requests, json

def movie_scrapper(search, movie_db):
    global calling
    config = open('config.json')
    config_json = json.load(config)
    header = config_json[movie_db]["header"]
    url = config_json[movie_db]["url"]
    header['path'] = header['path'].format(search)
    url = url.format(search)

    try:
        req = requests.get(url = url, headers = header)
    except:
        print("Error in loading data..")
        calling = 0
        return 0
    
    if req.status_code == 200:
        res = json.loads(req.content)
        if len(res) == 0:
            print("No matching result at {0} ", movie_db)
            calling = 0
            return 0
        else:
            functn = globals()[movie_db+"_db"]
            print(functn(search, res))
            calling = 1

def cinematerial_db(search, res):
    otpt = []
    search = search.split(' ')
    for i in range(len(res)):
        for j in range(len(search)):
            if res[i]['name'].lower().find(search[j]) != -1:
                otpt.append({'name':res[i]['name'], 'url':res[i]['url'], 'year':res[i]['year']})
                break
    if len(otpt) == 0:
        for i in range(len(res)):
            otpt.append({'name':res[i]['name'], 'url':res[i]['url'], 'year':res[i]['year']})
            if len(otpt) == 4:
                break

    print(otpt)
    calling = 1

def imdb_db(search, res):
    otpt = []
    search = search.split(' ')
    data = res["d"]
    for i in range(len(data)):
        for j in range(len(search)):
            if data[i]['l'].lower().find(search[j]) != -1:
                otpt.append({'name':data[i].get('l'), 'catgry':data[i].get('qid'), 'poster':data[i].get('i').get('imageUrl'), 'year':data[i].get('y')})
                break
    if len(otpt) == 0:
        for i in range(len(res)):
            otpt.append({'name':data[i].get('l'), 'catgry':data[i].get('qid'), 'poster':data[i].get('i').get('imageUrl'), 'year':data[i].get('y')})
            if len(otpt) == 4:
                break
    print(otpt)


movie_db = ['imdb']

for i in range(len(movie_db)):
    movie_scrapper(input('Enter the movie name :-').strip().lower(), movie_db[i])
    if calling:
        break
    
