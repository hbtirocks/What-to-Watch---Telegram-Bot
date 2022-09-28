import requests, json

def movie_scrapper(search, movie_db):
    config = open('config.json')
    config_json = json.load(config)
    header = config_json[movie_db]["header"]
    url = config_json[movie_db]["url"]
    header['path'] += search
    url += search

    try:
        req = requests.get(url = url, headers = header)
    except:
        print("Error in loading data..")
        return 0
    
    if req.status_code == 200:
        res = json.loads(req.content)
        otpt = []
        search = search.strip().lower().split(' ')
        for i in range(len(res)):
            for j in range(len(search)):
                if res[i]['name'].lower().find(search[j]) != -1:
                    otpt.append({'name':res[i]['name'], 'url':res[i]['url'], 'year':res[i]['year']})
                    break
        if len(otpt) < 2:
            for i in range(len(res)):
                if otpt[0]['url'] != res[i]['url']:
                    otpt.append({'name':res[i]['name'], 'url':res[i]['url'], 'year':res[i]['year']})
                if len(otpt) == 4:
                    break
        
    print(otpt)

movie_scrapper(input('Enter the movie name :-').strip())
