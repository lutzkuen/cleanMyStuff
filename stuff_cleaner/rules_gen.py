"""
Author: Lutz Künneke
Date: 2019-08-10

Rules generator
"""
import os
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier as clf
from sklearn.model_selection import train_test_split
import logging

class NotInitialized(Exception):
    pass

class RulesGenerator(object):

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.initialized = False
        self.features = []

    def set_data(self, data, target_column):
        self.target_column = target_column
        self.data = data

    def generate_features(self):
        for row in self.data:
            head = row['path']
            tail = head
            while head and tail:
                head, tail = os.path.split(head)
                if not tail in self.features and not '.' in tail:
                    self.logger.info('Adding Feature {feature}'.format(feature=tail))
                    # print('Adding Feature {feature}'.format(feature=tail))
                    self.features.append(tail)
                # print(head + ' -- ' + tail)
        self.df = []
        self.target = []
        self.logger.info('Generating Dataframe'.format(feature=tail))
        for row in self.data:
            row_dict = {feature: 0 for feature in self.features}
            head = row['path']
            tail = head
            while head and tail:
                head, tail = os.path.split(head)
                if tail in self.features:
                    row_dict[tail] = 1
            self.df.append(row_dict)
            self.target.append({self.target_column: row[self.target_column]})
        self.df = pd.DataFrame(self.df)
        self.target = pd.DataFrame(self.target)
        print('Features Generated: ' + str(self.df.shape))

    def train_model(self):
        # TODO make this more dynamic
        n_estimators = 5
        self.model = clf(n_estimators=n_estimators, n_iter_no_change=10, max_depth=1)
        # by settings n_iter_no_change sklearn will set aside another portion of the train set for validation
        x_train, x_test, y_train, y_test = train_test_split(self.df, self.target, test_size=0.1)
        self.model.fit(x_train, y_train)
        self.score = self.model.score(x_test, y_test)
        self.logger.info('Model trained with test accuracy: {accuracy}'.format(accuracy=str(self.score)))
        self.initialized = True

    def predict(self, path):
        if not self.initialized:
            raise(NotInitialized)
        row_dict = {feature: 0 for feature in self.features}
        head = path
        tail = head
        while head and tail:
            head, tail = os.path.split(head)
            if tail in row_dict.keys():
                row_dict[tail] = 1
        row_df = pd.DataFrame(row_dict, index=[0])
        pred = self.model.predict(row_df)
        return pred[0]