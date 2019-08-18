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
import configparser
import argparse
import time
import datetime

def last_access(filename):
    attime = max(os.path.getatime(filename), os.path.getmtime(filename))  # last access in secconds
    attime = time.localtime(attime)
    attime = datetime.datetime.fromtimestamp(time.mktime(attime))

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
                    if os.path.abspath(fullname) in master.blacklist:
                        continue
                    slave = CrawlerSlave(fullname, master)
            except Exception as e:
                print(str(e))
                raise(e)


class CrawlerMaster(object):

    def __init__(self, config_file):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        handler.setFormatter(log_formatter)
        self.logger.addHandler(handler)
        conf = configparser.ConfigParser()
        conf.read(config_file)
        self.blacklist = conf.get('file', 'blacklist').split(';')
        self.root = conf.get('file', 'root')
        self.record_source = conf.get('file', 'record_source')
        self.server = conf.get('file', 'server')

    def save_file(self, filename, update=False):
        post_url = self.server + '/v1/add_file'
        single_url = self.server + '/v1/file'
        test_file = {
            'full_path': os.path.abspath(filename),
            'record_source': self.record_source
        }
        r = requests.post(url=single_url, json=test_file)
        if len(r.json()['files']) > 0 and not update:
            self.logger.warning(
                '{path} already in database - skipping'.format(path=filename))
            return
        new_file = {
            'full_path': os.path.abspath(filename),
            'content_md5': md5(filename),
            'last_accessed': last_access(filename),
            'record_source': self.record_source
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
                if os.path.abspath(fullname) in self.blacklist:
                    continue
                slave = CrawlerSlave(fullname, self)
            else:
                self.save_file(fullname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Please provide a config file containing root directory and blacklist')
    parser.add_argument('--config',dest='config',help='Path to config file')
    args = parser.parse_args()
    if not args.config:
        parser.print_help()
    else:
        cl = CrawlerMaster(args.config)
        cl.crawl_root()
