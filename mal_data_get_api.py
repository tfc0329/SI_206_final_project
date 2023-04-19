import json
import requests
import secrets

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


if __name__ == '__main__':
    code_verifier = code_challenge = get_new_code_verifier()
    print_new_authorisation_url(code_challenge)

    authorisation_code = input('Copy-paste the Authorisation Code: ').strip()
    token = generate_new_token(authorisation_code, code_verifier)

    print_user_info(token['access_token'])