import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler

class UserPredictor:
    def fit(self, train_users, train_logs, train_clicked):
        model = Pipeline([
        ("pf", PolynomialFeatures(degree=5, include_bias=False)),
        ("std", StandardScaler()),
        ("lr", LogisticRegression(fit_intercept=False, max_iter=500)),
        ])
        self.analyze(train_users, train_logs, train_clicked)
        train_users["feature"] = self.dicty.values()
        xcols = train_users[["past_purchase_amt", "feature", "age"]]
        ycol = train_clicked["clicked"]
        self.model = model.fit(xcols, ycol)
        #return model.score(xcols, ycol)
    
    def predict(self, test_users, test_logs):
        dicty = {}
        for idnum in test_users["id"]:
            dicty[idnum] = 0
        logs = test_logs.set_axis(test_logs["id"])
        for idnum in logs["id"]:
            dicty[idnum] += logs.at[idnum, "duration"].sum()
        test_users["feature"] = dicty.values()
        return self.model.predict(test_users[["past_purchase_amt", "feature", "age"]])
    
    def analyze(self, test_users, train_logs, train_clicked):
        dicty = {}
        for idnum in train_clicked["id"]:
            dicty[idnum] = 0
        logs = train_logs.set_axis(train_logs["id"])
        for idnum in logs["id"]:
            dicty[idnum] += logs.at[idnum, "duration"].sum()
        self.dicty = dicty
