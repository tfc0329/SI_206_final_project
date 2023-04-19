import json
import requests
import secrets
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np



client_id = '8c8c1dab271e1bda5a7cfbc5ea1a9da8'
client_secret = '0a7a12ca30983542dea467738b9c48457dd1eba95bf8e0e9566fd45e5ad22332'

# 1. Generate a new Code Verifier / Code Challenge.
def get_new_code_verifier():

    token = secrets.token_urlsafe(100)
    return token[:128]

# 2. Print the URL needed to authorise your application.
def print_new_authorisation_url(code_challenge):
    global client_id

    url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={client_id}&code_challenge={code_challenge}'
    print(f'Authorise your application by clicking here: {url}\n')

# 3. Once you've authorised your application, you will be redirected to the webpage you've
#    specified in the API panel. The URL will contain a parameter named "code" (the Authorisation
#    Code). You need to feed that code to the application.
def generate_new_token(authorisation_code, code_verifier):
    global client_id, client_secret

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorisation_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the request contains errors

    token = response.json()
    response.close()
    print('Token generated successfully!')

    with open('token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in "token.json"')

    return token

# 4. Test the API by requesting your profile information
def print_user_info(access_token):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    user = response.json()
    response.close()

    print(f"\n>>> Greetings {user['name']}! <<<")


# if __name__ == '__main__':
#     code_verifier = code_challenge = get_new_code_verifier()
#     print_new_authorisation_url(code_challenge)

#     authorisation_code = input('Copy-paste the Authorisation Code: ').strip()
#     token = generate_new_token(authorisation_code, code_verifier)

#     print_user_info(token['access_token'])

def get_mal_ranking_data():
    popularity_url = 'https://api.myanimelist.net/v2/anime/ranking?ranking_type=bypopularity&limit=100'
    # -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImIzMTM4MjFhZjg4MzU0YTM4YmMxYWQ3NDQwMWJjM2Y3OWQ3MThhNzEzYzgwM2U3NmRhN2Y1NjllMzk0NTgzY2IyZDYzYjVjOGVhZjA3NzE3In0.eyJhdWQiOiI4YzhjMWRhYjI3MWUxYmRhNWE3Y2ZiYzVlYTFhOWRhOCIsImp0aSI6ImIzMTM4MjFhZjg4MzU0YTM4YmMxYWQ3NDQwMWJjM2Y3OWQ3MThhNzEzYzgwM2U3NmRhN2Y1NjllMzk0NTgzY2IyZDYzYjVjOGVhZjA3NzE3IiwiaWF0IjoxNjgxOTIwMDY2LCJuYmYiOjE2ODE5MjAwNjYsImV4cCI6MTY4NDUxMjA2Niwic3ViIjoiOTA1NTgwOCIsInNjb3BlcyI6W119.P0mERa0yA4WYoM90SPDOWxJ_Mt2effZGCowAShkbK4lC5P5rjJ1LNIow9noBHiXtdrrKuk74ISQFMqm4X7B0UchjqlkFDWf0BtU2ximIXgx1pb0R40MbA00taK58ViObziedGlmtcd5zGbWwtCtKc0LNP9_Fe0XuBE2Q4aq29fl9HlAuthBsvfkYzERg2F3UPeOMJEkJ5dpYsvj2umX-o_Z3eBKVApCuLO2i8JQA8yHbRp-6Ze0CKK76cx7VdvTZlvLn8-3bxas_kR8s6Y2frhP_aWp2yrR1NPq9FWjgZFyN5YBB6ZXSzp4SafphgCNTSnarS9zQJXFCwQvgwZN9zw'

    api_call_headers = {'Authorization': 'Bearer ' + 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImIzMTM4MjFhZjg4MzU0YTM4YmMxYWQ3NDQwMWJjM2Y3OWQ3MThhNzEzYzgwM2U3NmRhN2Y1NjllMzk0NTgzY2IyZDYzYjVjOGVhZjA3NzE3In0.eyJhdWQiOiI4YzhjMWRhYjI3MWUxYmRhNWE3Y2ZiYzVlYTFhOWRhOCIsImp0aSI6ImIzMTM4MjFhZjg4MzU0YTM4YmMxYWQ3NDQwMWJjM2Y3OWQ3MThhNzEzYzgwM2U3NmRhN2Y1NjllMzk0NTgzY2IyZDYzYjVjOGVhZjA3NzE3IiwiaWF0IjoxNjgxOTIwMDY2LCJuYmYiOjE2ODE5MjAwNjYsImV4cCI6MTY4NDUxMjA2Niwic3ViIjoiOTA1NTgwOCIsInNjb3BlcyI6W119.P0mERa0yA4WYoM90SPDOWxJ_Mt2effZGCowAShkbK4lC5P5rjJ1LNIow9noBHiXtdrrKuk74ISQFMqm4X7B0UchjqlkFDWf0BtU2ximIXgx1pb0R40MbA00taK58ViObziedGlmtcd5zGbWwtCtKc0LNP9_Fe0XuBE2Q4aq29fl9HlAuthBsvfkYzERg2F3UPeOMJEkJ5dpYsvj2umX-o_Z3eBKVApCuLO2i8JQA8yHbRp-6Ze0CKK76cx7VdvTZlvLn8-3bxas_kR8s6Y2frhP_aWp2yrR1NPq9FWjgZFyN5YBB6ZXSzp4SafphgCNTSnarS9zQJXFCwQvgwZN9zw'}
    api_call_popularity_response = requests.get(popularity_url, headers=api_call_headers)

    popularity_data = json.loads(api_call_popularity_response.text)

    new_dict = {}
    item_list = []

    for item in popularity_data['data']:

        item_dict = {}

        id = item['node']['id']
        item_dict['id'] = id

        details_url = f'https://api.myanimelist.net/v2/anime/{id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics'
        api_call_details_response = requests.get(details_url, headers=api_call_headers)
        details_data = json.loads(api_call_details_response.text)

        num_list_users = details_data['num_list_users']
        mean_score = details_data['mean']
        item_dict['popularity'] = num_list_users
        item_dict['mean_score'] = mean_score

        item_list.append(item_dict)

    new_dict['data'] = item_list

    return new_dict

def anilist_pull():
    # Here we define our query as a multi-line string
    query = '''
    query ($perPage: Int, $page: Int) {
        Page(perPage: $perPage, page: $page) {
            pageInfo {
                total
                perPage
                currentPage
                lastPage
                hasNextPage
            }
            media(sort: [SCORE_DESC]) {
                id
                idMal
                averageScore
                popularity
            }
        }
    }
    '''

    # Define the variables to be used in the query request
    variables = {
        'perPage': 50,
        'page': 1,
    }

    # Make the HTTP API request for the first page
    response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    data = json.loads(response.text)
    #print(data)

    # Update the variables to request the second page
    variables['page'] = 2

    # Make the HTTP API request for the second page
    response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    data2 = json.loads(response.text)

    return data, data2

def createBDfile(anilist_data1, anilist_data2):
    conn = sqlite3.connect("anilist_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS anilist_data
                 (id INTEGER PRIMARY KEY,
                 idMal INTEGER,
                 averageScore INTEGER,
                 popularity INTEGER)''')
    data_list = []
    for anilist_data in [anilist_data1, anilist_data2]:
        for media in anilist_data['data']['Page']['media']:
            data_list.append((media['id'], media['idMal'], media['averageScore'], media['popularity']))
    c.execute("CREATE TABLE IF NOT EXISTS anilist_data (id INTEGER PRIMARY KEY, idMAL INTERGER, averageScore INTERGER, popularity INTERGER)")
    conn.commit()
    conn.close()

def add_MAL_bd(malJSON):
    conn = sqlite3.connect("anilist_data.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS mal_data
                      (id INTEGER PRIMARY KEY, 
                      popularity INTEGER, 
                      mean_score REAL)''')

    # Parse the JSON and insert data into the table
    for item in json.loads(json.dumps(malJSON))['data']:
        cursor.execute(f"INSERT INTO mal_data (id, popularity, mean_score) VALUES (?, ?, ?)",
                       (item['id'], item['popularity'], item['mean_score']))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def scatter_avg_popularity(db_file):
    conn = sqlite3.connect(db_file)
    query = "SELECT idMAL, averageScore, popularity FROM anilist_data"
    df = pd.read_sql_query(query, conn)

    plt.style.use('dark_background')

    fig, ax = plt.subplots()
    ax.grid(True, linestyle='--')
    ax.set_axisbelow(True)
    ax.scatter(df["popularity"], df["averageScore"], color='red')
    ax.set_xlabel("Popularity")
    ax.set_ylabel("Average Score")
    ax.set_title("Anime Scores vs Popularity")
    
    
    z = np.polyfit(df["popularity"], df["averageScore"], 1)
    p = np.poly1d(z)
    ax.plot(df["popularity"], p(df["popularity"]), "r--")

    plt.show()

def main():
    anilistJSON1, anilistJSON2 = anilist_pull()
    #print(anilistJSON)
    createBDfile(anilistJSON1, anilistJSON2)
    malJSON = get_mal_ranking_data()
    add_MAL_bd(malJSON)
    #scatter_avg_popularity('anilist_data.db')
main()