import requests
import time
import json
import csv
import pandas as pd



# STEP 1: Scrap posts for a tag


arr = []

end_cursor = ''  # empty for the 1st page
tag = 'singapore'  # your tag
page_count = 1  # desired number of pages

for i in range(0, page_count):
    url = "https://www.instagram.com/explore/tags/{0}/?__a=1&max_id={1}".format(tag, end_cursor)
    # https://medium.com/@h4t0n/instagram-data-scraping-550c5f2fb6f1 --> instagram java interpretation

    #format 함수 https://blog.naver.com/kjk_lokr/221824321329 참조
    r = requests.get(url) # html
    data = json.loads(r.text)  # html.text to json format
    end_cursor = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info'][
        'end_cursor']  # value for the next page, 리스트 찾아들어가기
    edges = data['graphql']['hashtag']['edge_hashtag_to_media']['edges']  # list with posts

    for item in edges:
        arr.append(item['node']['shortcode'])

    print( i, "page crawled")
    time.sleep(2)  # insurence to not reach a time limit

print(end_cursor)  # save this to restart parsing with the next page

#dict을 json타입으로 변경하는 방법 = json.dumps() - 만들어서 보낼 때
#json 타입을 dict로 변경하는 방법 = json.loads() - 받아서 처리할 때

with open('posts.json', 'w') as outfile: # open ('파일명', 'w') 파일명의 파일을 만들고 write 하겠다
    json.dump(arr, outfile)  # save arr[] list  to json




# Step 2: Get locations for posts.


# Our new JSON data doesn’t contain locations.
with open('posts.json', 'r') as f:
    arr_cd = json.loads(f.read())  # load json data from previous step


locations = []


for shortcode in arr_cd:
    # where the shortcode is a unique combination of letters and numbers for every photo.
    url = "https://www.instagram.com/p/{0}/?__a=1".format(shortcode)
    # https://medium.com/@tiks.dev/scrap-instagram-locations-with-python-d48ba6e56ebc

    r = requests.get(url)
    try:  # try 는 오류가 났을때 except 을 실행하라는 구문이다
        data = json.loads(r.text)
        try:
            location = data['graphql']['shortcode_media']['location']['name']  # get location for a post
            if location != tag.title() :
                location_id = data['graphql']['shortcode_media']['location']['id'] # get location id for lat & lng
                print("location_crawl_success", location)

                # lat & lng
                id_url= "https://www.instagram.com/explore/locations/{0}/?__a=1".format(location_id)
                r_id = requests.get (id_url)
                lat = json.loads(r_id.text)['graphql']['location']['lat']
                lng = json.loads(r_id.text)['graphql']['location']['lng']
                print("lat&lng crawl success", lat, lng)
                locations.append({'shortcode': shortcode, 'location': location, 'id': location_id, "latitude": lat,
                                  "longitude": lng})

        except:
            location = ''  # if location is NULL
            location_id = ''
            lat = ''
            lng = ''
    except:
        location = ''

with open('locations.json', 'w') as outfile:
    json.dump(locations, outfile)  # save to json


# Step 3: Get number of locations
with open('locations.json', 'r') as f:
    arr = json.loads(f.read())  # load json data from previous step
    locationDict = {};
    for post in arr:
        location = post['location']
        # print(location)
        # print(locationDict)
        # print(location in locationDict)

        if (location and location in locationDict):
            locationDict[location] += 1
        elif (location):
            locationDict[location] = 1;

    # print(locationDict);

    df = pd.DataFrame.from_dict(locationDict, orient='index')
    df.to_excel('file.xls')


