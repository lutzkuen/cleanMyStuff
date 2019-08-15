"""
Author: Lutz Künneke
Date: 2019-089-10

This file contains the main classes that power the crawler
"""

import os
import sys
import numpy as np
import dataset
import code
from stuff_cleaner import rules_gen
import logging
import time
import datetime
import dataset
import filecmp


class CrawlerSlave(object):

    def __init__(self, directory, master):
        self.directory = directory
        self.file_endings = []
        self.logger = logging.getLogger()
        self.at_arr = []
        self.numfiles = 0
        now = datetime.datetime.now()
        try:
            files = os.listdir(directory)
        except Exception as e:
            self.logger.error(str(e))
            return
        for file in files:
            try:
                fullname = os.path.join(directory, file)
                if os.path.isfile(fullname):
                    master.compare_to_known_files(fullname)
                    fname, fext = os.path.splitext(fullname)
                    self.numfiles += 1
                    if not fext == '':
                        self.file_endings.append(fext)
                    attime = max(os.path.getatime(fullname), os.path.getmtime(fullname)) # last access in secconds
                    attime = time.localtime(attime)
                    attime = datetime.datetime.fromtimestamp(time.mktime(attime))
                    tdelta = now - attime
                    master.eval_file(fullname, tdelta)
                    self.at_arr.append(tdelta)
                else:
                    slave = CrawlerSlave(fullname, master)
                    if len(slave.at_arr) > 0:
                        self.at_arr.append(np.min(slave.at_arr))
                    self.numfiles += slave.numfiles
                    [self.file_endings.append(en) for en in slave.file_endings]
            except Exception as e:
                print(str(e))
                raise(e)
                # code.interact(banner='', local=locals())
        master.eval_slave(self)


class CrawlerMaster(object):

    def __init__(self, directory, db_path='sqlite:///crawler.db', skip_threshold=0.1):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.ERROR)
        handler = logging.StreamHandler(sys.stdout)
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        handler.setFormatter(logFormatter)
        self.logger.addHandler(handler)
        self.root = directory
        self.current = self.root
        self.maxtime = 6*30 # 6 months time
        self.logger.info('Connection to database {dbname}'.format(dbname=db_path))
        self.db = dataset.connect(db_path)
        self.del_model = rules_gen.RulesGenerator()
        self.init_del_model()
        # create to store info about files while crawling
        self.known_files = []
        self.skip_threshold = skip_threshold
        self.last_train = 0

    def init_del_model(self):
        """
        Initialize the model to predict whether a path is to be deleted

        :return: None
        """
        data = [line for line in self.db['deletion'].all()]
        # sprinkle in some positive lines to prevent all being at 0
        for i in range(max(20, int(len(data)/5))):
            in_line = data[np.random.randint(len(data))]
            data.append({'path': in_line['path'], 'del': 1})
        self.logger.info('Pushing data to deletion model')
        self.del_model.set_data(data, 'del')
        self.logger.info('Generating Features for deletion model')
        self.del_model.generate_features()
        self.logger.info('Training the deletion model')
        self.del_model.train_model()

    def crawl_root(self):
        files = os.listdir(self.root)
        file_endings = []
        now = datetime.datetime.now()
        for file in files:
            fullname = os.path.join(self.root, file)
            if os.path.isdir(fullname):
                try:
                    slave = CrawlerSlave(fullname, self)
                    if len(slave.at_arr) > 0:
                        attime = np.min(slave.at_arr)
                    else:
                        attime = 0
                except Exception as e:
                    print(str(e))
                    raise(e)
            else:
                if self.compare_to_known_files(fullname):
                    continue
                fname, fext = os.path.splitext(fullname)
                if not fext == '':
                    file_endings.append(fext)
                attime = max(os.path.getatime(fullname), os.path.getmtime(fullname))  # last access in secconds
                attime = time.localtime(attime)
                attime = datetime.datetime.fromtimestamp(time.mktime(attime))
                tdelta = now - attime
                self.eval_file(fullname, tdelta)
                # attime = min(os.path.getatime(fullname), os.path.getmtime(fullname))
            # if attime > self.maxtime:
            #     self.logger.info('Stale dir ' + str(fullname) + ' Last Access ' + sec_to_string(attime))

    def compare_to_known_files(self, filename):
        for f in self.known_files:
            self.logger.debug('Comparing {f1} to {f2}'.format(f1=f, f2=filename))
            if filecmp.cmp(f, filename):
                self.logger.info('Files {f1} and {f2} seem to be identical'.format(f1=f, f2=filename))
                return
        self.known_files.append(filename)
        return 0

    def query_deletion(self, directory, reason):
        del_tab = self.db['deletion']
        predicted_answer = self.del_model.predict(directory)
        if predicted_answer < self.skip_threshold: # if we are sure enough that there is no deletion just skip it
            self.logger.warning('{reason} -- {dir} was skipped ({predicted_answer})'.format(reason=reason, dir=directory, predicted_answer=predicted_answer))
            return 0
        if predicted_answer > 0.5:
            pred_answer = 'Y'
        else:
            pred_answer = 'N'
        answer = input('{reason} - delete {dir} ((Y)es/(N)o/(D)etails (predicted: {predicted}) )'.format(dir=directory, reason=reason, predicted=pred_answer))
        self.last_train += 1
        if self.last_train > 10:
            self.logger.info('Retraining Model')
            self.init_del_model()
            self.last_train = 0
        if answer.lower() in ['y', 'j', 'yes', 'ja']:
            del_tab.upsert({'path': directory, 'del': 1}, ['path'])
            return 1
        else:
            del_tab.upsert({'path': directory, 'del': 0}, ['path'])
            return 0

    def eval_slave(self, slave):
        if slave.numfiles == 0:
            if self.query_deletion(slave.directory, 'Empty Directory'):
                os.removedirs(slave.directory)