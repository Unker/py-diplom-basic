import requests
from pprint import pprint

BASE_URL = 'https://api.vk.com/method/'
API_VER = '5.131'


class VkUser:
    base_url = BASE_URL

    def __init__(self, token, api_ver):
        self.params = {
            'access_token': token,
            'v': api_ver,
        }

    def get_photos(self,
                    user_ids: str,
                    return_system: int = 0):
        url = self.base_url + 'friends.getLists'
        # url = self.base_url + 'users.get'
        params = {
            'user_ids': user_ids,
            'return_system': return_system,
        }
        params.update(self.params)
        print(url)
        print(params)
        response = requests.get(url, params=params)
        print(response)
        pprint(response.json())


if __name__ == '__main__':
    with open('Token.txt', 'r') as f:
        token = f.read().strip()
    print(token)
    user1 = VkUser(token=token, api_ver=API_VER)
    # user1.get_friends(user_ids='1,2')
