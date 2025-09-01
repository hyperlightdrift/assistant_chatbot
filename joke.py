import requests
from requests.exceptions import HTTPError


def tell_joke():
    try:
        headers = {"Accept": "application/json"}
        response = requests.get("https://icanhazdadjoke.com/", headers=headers)
        #look into params to customize get requests
        #look into headers to also customize get results
        response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    else:
        joke_data = response.json()
        print(f"{joke_data['joke']}\n")