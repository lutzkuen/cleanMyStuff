"""
Author: Lutz Künneke
Date: 2019-089-10

This file contains the main classes that power the crawler
"""

import os
import sys
import logging
import requests
import hashlib

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class CrawlerSlave(object):

    def __init__(self, directory, master):
        self.directory = directory
        self.file_endings = []
        self.logger = logging.getLogger()
        self.at_arr = []
        try:
            files = os.listdir(directory)
        except Exception as e:
            self.logger.error(str(e))
            return
        for file in files:
            try:
                fullname = os.path.join(directory, file)
                if os.path.isfile(fullname):
                    master.save_file(fullname)
                else:
                    slave = CrawlerSlave(fullname, master)
            except Exception as e:
                print(str(e))
                raise(e)


class CrawlerMaster(object):

    def __init__(self, directory):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        handler.setFormatter(logFormatter)
        self.logger.addHandler(handler)
        self.root = directory
        self.current = self.root

    def save_file(self, filename):
        post_url = 'http://127.0.0.1:5000/v1/add_file'
        new_file = {
            'full_path': os.path.abspath(filename),
            'content_md5': md5(filename),
            'record_source': 'HDD_LINUX'
        }
        r = requests.post(url=post_url, json=new_file)
        if r.status_code == 201:
            self.logger.info('Posted {path} to API'.format(path=filename))
        else:
            self.logger.warning('Response code {status} while posting {path}'.format(status=r.status_code, path=filename))

    def crawl_root(self):
        files = os.listdir(self.root)
        for file in files:
            fullname = os.path.join(self.root, file)
            if os.path.isdir(fullname):
                slave = CrawlerSlave(fullname, self)
            else:
                self.save_file(fullname)

if __name__ == '__main__':
    cl = CrawlerMaster('../..')
    cl.crawl_root()
