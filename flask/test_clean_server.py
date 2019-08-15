"""
Test file for the clean_server.py server
"""

import unittest
import requests

class ServerNotStarted(Exception):
    pass


class TestServer(unittest.TestCase):

    def setUp(self) -> None:
        # make sure the server is running
        test_url = 'http://127.0.0.1:5000'
        r = requests.get(url=test_url)

    def test_create_file(self):
        # push a single item
        new_file = {
            'path': 'TEST_PATH',
            'content': 'TEST_CONTENT',
            'device': 'TEST'
        }
        post_url = 'http://127.0.0.1:5000/v1/files'
        get_url = post_url
        r = requests.post(url=post_url, json=new_file)
        self.assertEqual(r.status_code, 201)
        # check if we get the file back
        r = requests.get(url=get_url)
        self.assertEqual(r.status_code, 200)
        res = r.json()
        found_line = False
        print(res)
        for line in res['files']:
            if line['path'] == new_file['path']:
                found_line = True
        self.assertTrue(found_line)
        get_single = get_url + '/TEST_PATH'
        r = requests.get(url=get_single)
        self.assertEqual(r.json()['files'][0]['path'], new_file['path'])
        self.assertEqual(r.status_code, 200)
        del_url = 'http://127.0.0.1:5000/v1/remove_file/TEST_PATH'
        r = requests.get(url=del_url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['removed'])
        # now make sure the line is gone
        r = requests.get(url=get_url)
        self.assertEqual(r.status_code, 200)
        res = r.json()
        found_line = False
        for line in res['files']:
            if line['path'] == new_file['path']:
                found_line = True
        self.assertFalse(found_line)

    def test_removal(self):
        del_url = 'http://127.0.0.1:5000/v1/remove_file/TEST_PATH'
        r = requests.get(url=del_url)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()['removed'])


if __name__ == '__main__':
    unittest.main()