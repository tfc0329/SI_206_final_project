import json
import requests
import secrets
import sqlite3
import os

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
        num_episodes = details_data['num_episodes']
        item_dict['popularity'] = num_list_users
        item_dict['mean_score'] = mean_score
        item_dict['num_episodes'] = num_episodes

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
                episodes
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
                 popularity INTEGER,
                 episodes INTERGER)''')
    data_list = []
    for anilist_data in [anilist_data1, anilist_data2]:
        for media in anilist_data['data']['Page']['media']:
            data_list.append((media['id'], media['idMal'], media['averageScore'], media['popularity'], media['episodes']))

    c.execute("SELECT MAX(id) FROM anilist_data")
    last_id = c.fetchone()[0] or 0

    num_rows_to_add = 100
    for i in range(num_rows_to_add):
        if i + last_id >= len(data_list):
            break
        c.execute("INSERT OR IGNORE INTO anilist_data (id, idMal, averageScore, popularity, episodes) VALUES (?, ?, ?, ?, ?)",
                   (last_id+i+1, data_list[last_id+i][1], data_list[last_id+i][2], data_list[last_id+i][3], data_list[last_id+i][4]))

    conn.commit()
    conn.close()

def add_MAL_bd(malJSON):
    conn = sqlite3.connect("anilist_data.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS mal_data
                      (row_id INTEGER PRIMARY KEY,
                      id INTEGER, 
                      popularity INTEGER, 
                      mean_score REAL,
                      num_episodes INTEGER)''')

    data_list = []
    for MAL_data2 in [malJSON]:
        for data in MAL_data2['data']:
            data_list.append((data['id'], data['popularity'], data['mean_score'], data['num_episodes']))

    # Get the last ID in the table
    cursor.execute("SELECT MAX(row_id) FROM mal_data")
    last_id = cursor.fetchone()[0] or 0

    # Parse the JSON and insert data into the table
    num_rows_to_add = 100
    for i in range(num_rows_to_add):
        if i + last_id >= len(data_list):
            break
        cursor.execute("INSERT OR IGNORE INTO mal_data (row_id, id, popularity, mean_score, num_episodes) VALUES (?, ?, ?, ?, ?)", 
                       ([last_id+i+1, data_list[last_id+i][0], data_list[last_id+i][1], data_list[last_id+i][2], data_list[last_id+i][3]]))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def add_data_join():
    conn = sqlite3.connect("anilist_data.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS data_join
                      (id INTEGER PRIMARY KEY,
                      num_episodes INTEGER,
                      mean_score REAL,
                      episodes INTEGER,
                      averageScore REAL)''')

    # Get the last ID in the table
    cursor.execute("SELECT MAX(id) FROM data_join")
    last_id = cursor.fetchone()[0] or 0

    # Join mal_data and anilist_data tables on idMAL
    query = f'''INSERT INTO data_join (id, num_episodes, mean_score, episodes, averageScore)
                SELECT mal_data.id AS idMAL, mal_data.num_episodes, mal_data.mean_score, 
                       anilist_data.episodes, anilist_data.averageScore 
                FROM mal_data JOIN anilist_data ON mal_data.id = anilist_data.idMAL 
                WHERE mal_data.id > {last_id} ORDER BY mal_data.id'''

    # Execute query and insert data into the table
    cursor.execute(query)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def SaveJsons(json_list):
    with open(os.path.join(os.path.dirname(__file__), "json_output.txt"), 'w') as f:
        for json_obj in json_list:
            if isinstance(json_obj, dict):
                json_string = json.dumps(json_obj)
            else:
                json_string = json_obj
            f.write(json_string + '\n')


def scatter_avg_popularity_COMBINED(db_file):
    conn = sqlite3.connect(db_file)
    query_anilist = "SELECT idMAL, averageScore, popularity FROM anilist_data"
    query_mal = "SELECT popularity, mean_score FROM mal_data"
    df_anilist = pd.read_sql_query(query_anilist, conn)
    df_anilist['averageScore'] = df_anilist['averageScore'] / 10
    df_mal = pd.read_sql_query(query_mal, conn)
    df_mal['averageScore'] = df_mal['popularity'] * 10000

    plt.style.use('dark_background')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,6))
    ax1.grid(True, linestyle='--')
    ax1.set_axisbelow(True)
    ax1.scatter(df_anilist["popularity"], df_anilist["averageScore"], color='gold')
    ax1.set_xlabel("Popularity")
    ax1.set_ylabel("Average Score")
    ax1.set_title("Manga Scores vs Popularity")
    ax1.set_ylim(6.5, 9.4)

    z1 = np.polyfit(df_anilist["popularity"], df_anilist["averageScore"], 1)
    p1 = np.poly1d(z1)
    ax1.plot(df_anilist["popularity"], p1(df_anilist["popularity"]), "r--")

    ax2.grid(True, linestyle='--')
    ax2.set_axisbelow(True)
    ax2.scatter(df_mal["popularity"], df_mal["mean_score"], color='blue')
    ax2.set_xlabel("Popularity")
    ax2.set_ylabel("Average Score")
    ax2.set_title("Anime Scores vs Popularity")
    ax2.set_ylim(6.5, 9.4)

    z2 = np.polyfit(df_mal["popularity"], df_mal["mean_score"], 1)
    p2 = np.poly1d(z2)
    ax2.plot(df_mal["popularity"], p2(df_mal["popularity"]), "r--")

    plt.tight_layout()
    plt.show()

def scatter_avg_popularity(db_file):
    conn = sqlite3.connect(db_file)
    query_anilist = "SELECT idMAL, averageScore, popularity FROM anilist_data"
    query_mal = "SELECT popularity, mean_score FROM mal_data"
    df_anilist = pd.read_sql_query(query_anilist, conn)
    df_anilist['averageScore'] = df_anilist['averageScore'] / 10
    df_mal = pd.read_sql_query(query_mal, conn)
    df_mal['averageScore'] = df_mal['popularity'] * 10000

    plt.style.use('dark_background')

    fig, ax = plt.subplots(1, 1, figsize=(12,6))
    ax.grid(True, linestyle='--')
    ax.set_axisbelow(True)
    ax.scatter(df_anilist["popularity"], df_anilist["averageScore"], color='gold', label='Manga')
    ax.scatter(df_mal["popularity"], df_mal["mean_score"], color='blue', label='Anime')
    ax.set_xlabel("Popularity")
    ax.set_ylabel("Average Score")
    ax.set_title("Anime and Manga Scores vs Popularity")
    ax.set_ylim(6.5, 9.4)
    ax.legend()

    z1 = np.polyfit(df_anilist["popularity"], df_anilist["averageScore"], 1)
    p1 = np.poly1d(z1)
    ax.plot(df_anilist["popularity"], p1(df_anilist["popularity"]), "y--")

    z2 = np.polyfit(df_mal["popularity"], df_mal["mean_score"], 1)
    p2 = np.poly1d(z2)
    ax.plot(df_mal["popularity"], p2(df_mal["popularity"]), "b--")

    plt.tight_layout()
    plt.show()

def plot_data_join(db_file):
    # Connect to database and read data_join table
    conn = sqlite3.connect(db_file)
    query = "SELECT num_episodes+episodes as num_total_episodes, mean_score, averageScore/10 as average_score FROM data_join"
    df = pd.read_sql(query, conn)
    
    # Create scatter plot with trend line
    g = sns.lmplot(x="mean_score", y="num_total_episodes", data=df, height=7, scatter_kws={'color': 'green'}, line_kws={'color': 'red'})

    # Set plot properties
    g.set_axis_labels("Mean Score", "Total Number of Episodes")
    g.fig.suptitle("Relationship Between Mean Score and Total Number of Episodes")
    g.fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    g.ax.grid(True)
    plt.style.use('dark_background')
    plt.show()


def main():
    anilistJSON1, anilistJSON2 = anilist_pull()
    #print(anilistJSON1, anilistJSON2)
    createBDfile(anilistJSON1, anilistJSON2)
    malJSON = get_mal_ranking_data()
    #print(malJSON)
    add_MAL_bd(malJSON)
    add_data_join()
    SaveJsons([anilistJSON1, anilistJSON2, malJSON])
    scatter_avg_popularity('anilist_data.db')
    scatter_avg_popularity_COMBINED('anilist_data.db')
    plot_data_join('anilist_data.db')
main()