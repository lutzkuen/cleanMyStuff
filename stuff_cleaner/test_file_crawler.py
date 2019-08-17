"""

"""

import unittest
import os
from stuff_cleaner import file_crawler
import requests


class TestCrawlerSlave(unittest.TestCase):

    def setUp(self) -> None:
        self.test_directory = '/tmp/crawler_unittest'
        self.test_configfile = '/tmp/crawler_test.conf'
        f = open(self.test_configfile, 'w')
        f.write('[file]\n')
        f.write('blacklist: NONE\n')
        f.write('root: {root}\n'.format(root=self.test_directory))
        f.close()
        self.test_file = os.path.join(self.test_directory, 'test_file')
        if os.path.isdir(self.test_directory):
            os.system('rm -rf {path}'.format(path=self.test_directory))
        os.mkdir(self.test_directory)
        os.system('touch {testfile}'.format(testfile=self.test_file))
        self.master = file_crawler.CrawlerMaster(self.test_configfile)

    def test_init(self):
        url_single = 'http://127.0.0.1:5000/v1/file'
        url_remove = 'http://127.0.0.1:5000/v1/remove_file'
        file_id = {
            'full_path': self.test_file
        }
        slave = file_crawler.CrawlerSlave(self.test_directory, self.master)
        r = requests.post(url=url_single, json=file_id)
        self.assertEqual(r.json()['files'][0]['full_path'], self.test_file)
        self.assertEqual(r.json()['files'][0]['content_md5'], file_crawler.md5(self.test_file))
        self.assertEqual(r.status_code, 200)
        # delete the file from database
        r = requests.post(url=url_remove, json=file_id)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['removed'])

    def tearDown(self) -> None:
        os.system('rm -rf {path}'.format(path=self.test_directory))
        os.remove(self.test_configfile)


class TestCrawlerMaster(unittest.TestCase):

    def setUp(self) -> None:
        self.test_directory = '/tmp/crawler_unittest'
        self.test_configfile = '/tmp/crawler_test.conf'
        f = open(self.test_configfile, 'w')
        f.write('[file]\n')
        f.write('blacklist: NONE\n')
        f.write('root: {root}\n'.format(root=self.test_directory))
        f.close()
        self.test_file = os.path.join(self.test_directory, 'test_file')
        if os.path.isdir(self.test_directory):
            os.system('rm -rf {path}'.format(path=self.test_directory))
        os.mkdir(self.test_directory)
        os.system('touch {testfile}'.format(testfile=self.test_file))
        self.master = file_crawler.CrawlerMaster(self.test_configfile)

    def test_crawl_root(self):
        self.master.crawl_root()
        url_single = 'http://127.0.0.1:5000/v1/file'
        url_remove = 'http://127.0.0.1:5000/v1/remove_file'
        file_id = {
            'full_path': self.test_file
        }
        slave = file_crawler.CrawlerSlave(self.test_directory, self.master)
        r = requests.post(url=url_single, json=file_id)
        self.assertEqual(r.json()['files'][0]['full_path'], self.test_file)
        self.assertEqual(r.json()['files'][0]['content_md5'], file_crawler.md5(self.test_file))
        self.assertEqual(r.status_code, 200)
        # delete the file from database
        r = requests.post(url=url_remove, json=file_id)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['removed'])

    def tearDown(self) -> None:
        os.system('rm -rf {path}'.format(path=self.test_directory))
        os.remove(self.test_configfile)