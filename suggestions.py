import requests, json

def movie_suggestions(search):
    #...............Code for generating search url from input.............
    url = 'https://www.cinematerial.com/search?q='+search
    
    #..............Code for fetching suggestions.................................
    
    headers = {
        'authority': 'www.cinematerial.com',
        'method': 'GET',
        'path': '/search?q=',
        'scheme': 'https',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_ga=GA1.2.94375735.1664129867; _gid=GA1.2.160034257.1664234651; PHPSESSID=19qgfg1dr8hv75vpc8cujpmnt4; XSRF-TOKEN='+
        'eyJpdiI6IndGWnFiRnFiTm43WDhBTmoxcU9reXc9PSIsInZhbHVlIjoiUUdBM2crUS92WFRpczY5M3VKMnJXeEY1VUd2Rmk0Q1MwcjIvWWRiWUVsL0pqSVVnUXhTT'+
        'C8zeFlMSEpzeFRXb1dQaFVQOHZ4YWlZVzJKWGVlVVNQRFZRN1dYQ0piOU1vdnUycVVyOW1vUUVmYVozd2Y0eWlNVHZ3ZlBZN2l3aHMiLCJtYWMiOiI2ZjE2MGI0MTI3'+
        'Mjk2MmY5YWZlMGUzZjkwMjAxMTU2YmZiNTdiOTVlYzc4ZThmMGU0ZmI4ZDVmZTJjZDAzYWIwIiwidGFnIjoiIn0%3D; cmsession19=eyJpdiI6IlZHOWFGYnBCQ2RoS'+
        'GVaN3F5QmtGS0E9PSIsInZhbHVlIjoib2E2d2ltbEFmbUhwMmp2NGsyeG9VQ2NoWkk1TSsrWEJUTjhRWHBNS0tObllDRXh3dTFHNFdSZ1FhN0RoblU1ekVoVmdHSlYzc29'+
        'ZUFJRRWVHM05mR0IyV0xQVFhXWHcyb09Na05JUm9ISEkycDhVUzM2aGIzK29QdDNhcDU5OFoiLCJtYWMiOiI2MTZlYjFmOWRiYmUzZjZkNWU3ODc0NzMyNGZjN2ZiMDY3NTl'+
        'jZjMyMWI2MDY5MmQwZGE2YWMyZjAzNjdlNzQ2IiwidGFnIjoiIn0%3D; _gat_gtag_UA_2030970_19=1',
        'referer': 'https://www.cinematerial.com/',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }

    headers['path'] = headers['path']+search
    try:
        req = requests.get(url = url, headers = headers)
    except:
        #code to be executed

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

movie_suggestions(input('Enter the movie name :-').strip())
