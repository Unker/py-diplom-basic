import unittest
import requests
from main import YaDiskApi
from main import TOKEN_YA
from datetime import datetime

FOLDER = "Netology1/test/"


class TestYaDiskApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls. disk = YaDiskApi(TOKEN_YA)

    def test_create_folder_on_ya_disk(self):
        folder = FOLDER + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # folder = FOLDER
        # проверим существование каталога
        resources_url = self.disk.base_url + "/v1/disk/resources"
        params = {"path": folder}
        headers = self.disk._get_header()
        response = requests.get(resources_url, headers=headers, params=params)
        self.assertEqual(response.status_code, 404)
        # создадим каталог
        response = self.disk.create_folder_on_ya_disk(folder=folder)
        self.assertEqual(response.status_code, 201)
        # проверим что каталог действительно создался
        response = requests.get(resources_url, headers=headers, params=params)
        self.assertEqual(response.status_code, 200)
        # удалим созданый каталог
        params = {"path": folder, "permanently": True}
        response = requests.delete(resources_url, headers=headers, params=params)
        sc = response.status_code
        is_deleted = False
        if sc == 204 or sc == 202:
            is_deleted = True
        self.assertTrue(is_deleted, msg="Error while delete file")
        # проверим что каталог удален
        params = {"path": folder}
        response = requests.get(resources_url, headers=headers, params=params)
        self.assertEqual(response.status_code, 404)

