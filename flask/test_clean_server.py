"""
Test file for the clean_server.py server
"""

import unittest
import requests
import logging
import sys

class ServerNotStarted(Exception):
    pass


class TestServer(unittest.TestCase):

    def setUp(self) -> None:
        # make sure the server is running
        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)
        handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        handler.setFormatter(log_formatter)
        logger.addHandler(handler)
        logger.info('Logger set up')
        test_url = 'http://127.0.0.1:5000'
        r = requests.get(url=test_url)
        logger.info('Test server is alive')

    def test_create_file(self):
        # push a single item
        logger = logging.getLogger()
        new_file = {
            'full_path': 'TEST_PATH',
            'content_md5': 'TEST_CONTENT',
            'record_source': 'TEST',
            'last_accessed': '2019-03-29'
        }
        url_all = 'http://127.0.0.1:5000/v1/files'
        url_single = 'http://127.0.0.1:5000/v1/file'
        url_add = 'http://127.0.0.1:5000/v1/add_file'
        url_remove = 'http://127.0.0.1:5000/v1/remove_file'
        r = requests.post(url=url_add, json=new_file)
        self.assertEqual(r.status_code, 201)
        # check if we get the file back
        r = requests.get(url=url_all)
        self.assertEqual(r.status_code, 200)
        res = r.json()
        found_line = False
        logger.info(res)
        for line in res['files']:
            if line['full_path'] == new_file['full_path']:
                found_line = True
        self.assertTrue(found_line)
        r = requests.post(url=url_single, json=new_file)
        print(r.json())
        self.assertEqual(r.json()['files'][0]['full_path'], new_file['full_path'])
        self.assertEqual(r.status_code, 200)
        r = requests.post(url=url_remove, json=new_file)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['removed'])
        # now make sure the line is gone
        r = requests.get(url=url_all)
        self.assertEqual(r.status_code, 200)
        res = r.json()
        found_line = False
        for line in res['files']:
            if line['full_path'] == new_file['full_path']:
                found_line = True
        self.assertFalse(found_line)

    def test_removal(self):
        del_url = 'http://127.0.0.1:5000/v1/remove_file'
        new_file = {
            'full_path': 'TEST_PATH'    ,
            'content_md5': 'TEST_CONTENT',
            'record_source': 'TEST'
        }
        r = requests.post(url=del_url, json=new_file)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()['removed'])


if __name__ == '__main__':
    unittest.main()
