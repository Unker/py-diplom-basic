import requests
from pprint import pprint
import os
from dotenv import load_dotenv
from tqdm import tqdm
import json

BASE_VK_URL = 'https://api.vk.com/method/'
API_VK_VER = '5.131'
BASE_YA_URL = "https://cloud-api.yandex.net:443"

load_dotenv()
TOKEN_VK = os.getenv('TOKEN_VK')
TOKEN_YA = os.getenv('TOKEN_YA')


class YaDiskApi:
    base_url = BASE_YA_URL

    def __init__(self, token: str):
        self.token = token

    def _get_header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def _get_upload_link(self, dst_path: str):
        """Получить ссылку на яндекс диск для загрузки файла"""
        upload_url = self.base_url + "/v1/disk/resources/upload"
        headers = self._get_header()
        params = {"path": dst_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response

    def upload_file(self, dst_path: str, file: str):
        """Метод загружает файл на яндекс диск"""
        href_json = self._get_upload_link(dst_path).json()
        href = href_json["href"]
        response = requests.put(href, data=file)
        response.raise_for_status()
        if response.status_code == 201:
            print(f"Success upload file on Disk {dst_path}")

    def upload_file_from_url(self,
                              src_path: str,
                              dst_path: str,
                              verbose: bool = False):
        """загружает файл на яндекс диск по url"""
        upload_url = self.base_url + "/v1/disk/resources/upload"
        self.create_path_on_ya_disk(dst_path, verbose=verbose)
        params = {
            "path": dst_path,
            "url": src_path,
            "fields": "name"
        }
        headers = self._get_header()
        response = requests.post(upload_url, headers=headers, params=params)
        if verbose:
            print(response)
        response.raise_for_status()
        if response.status_code == 201:
            print("Success")
        return response

    def create_path_on_ya_disk(self, folders: str, verbose: bool = False):
        sub_path = ''
        folders = os.path.split(path)
        for folder in folders:
            sub_path = sub_path + '/' + folder
            self.create_folder_on_ya_disk(sub_path, verbose=verbose)

    def create_folder_on_ya_disk(self, folder: str, verbose: bool = False):
        resources_url = self.base_url + "/v1/disk/resources"
        params = {"path": folder}
        headers = self._get_header()
        response = requests.get(resources_url, headers=headers, params=params)
        # print(response)
        # если нет каталога, то создадим его
        if response.status_code == 404:
            if verbose:
                print(f"Trying to create folder {folder}")
            response = requests.put(resources_url, headers=headers, params=params)
            # print(response)
            if verbose:
                if response.status_code == 201:
                    print(f"The folder '{folder}' has created")
                else:
                    print(f"Error {response.status_code}")

        return response


class VkApi:
    base_url = BASE_VK_URL

    def __init__(self, token, api_ver):
        self.params = {
            'access_token': token,
            'v': api_ver,
        }

    def get_photos(self,
                   owner_id: str = '',
                   album_id: str = 'profile',
                   extended: bool = 1,
                   photo_sizes: bool = 1,
                   count: int = 5,
                   verbose: bool = False
                   ) -> dict:
        '''Возвращает список фотографий в альбоме'''
        url = self.base_url + 'photos.get'
        params = {}
        params.update(self.params)
        if owner_id:
            params['owner_id'] = owner_id
        params.update({
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': count,
        })
        response = requests.get(url, params=params)
        if response.status_code == 200:
            ret = response.json()['response']['items']
            cnt = response.json()['response']['count']
            if cnt < count:
                print("WARNING. Objects received less than requested")
                print(f"Expected {count}, received {cnt}")
            if verbose:
                pprint(response.json())
        else:
            if verbose:
                print(response)
            ret = None

        return ret


def get_info_max_sz_photo(photos_items: list):
    '''
    Поиск изображения с максимальным размером.
    Заполнение структуры с информацией об этом фото
    '''
    photos = []
    names = []
    for item in photos_items:
        max_img = item['sizes'][-1]
        name = str(item['likes']['count'])
        if name in names:
            name = f"{name}_{item['date']}"

        names.append(name)
        max_img.update({'file_name': name + '.jpg'})
        photos.append(max_img)

    return photos


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


if __name__ == '__main__':
    owner_id = input("Enter VK User ID:")
    if not check_int(owner_id):
        print("ID not integer")
        exit()
    # grab photos url from VK
    user1 = VkApi(token=TOKEN_VK, api_ver=API_VK_VER)
    photos_json = user1.get_photos(owner_id=owner_id, verbose=False)
    max_sz_photos = get_info_max_sz_photo(photos_json)
    # save photos to YaDisk
    disk = YaDiskApi(TOKEN_YA)
    path = "Netology1/test"
    info = []
    print("Uploading photos...")
    for photo in tqdm(max_sz_photos):
        dst_path = path + '/' + photo['file_name']
        src_path = photo['url']
        resp = disk.upload_file_from_url(src_path=src_path, dst_path=dst_path, verbose=False)
        if resp.status_code == 202:
            info.append(photo)
    print("Done")
    # Добавить информацию о загруженных файлах
    json_object = json.dumps(max_sz_photos, indent=4)
    dst_path = path + '/' + 'info.json'
    disk.upload_file(dst_path=dst_path, file=json_object)
