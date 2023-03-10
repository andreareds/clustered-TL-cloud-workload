"""
Suppor Vector Regressor (SVR) predictive model with shared functionalities
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.model_selection import TimeSeriesSplit
from models.model_interface import ModelInterface


class SVR(ModelInterface):
    def __init__(self, name):
        """
        Constructor of the Model Interface class
        :param name: string: name of the model
        """
        super().__init__(name)
        self.p = {'kernel': 'rbf',
                  'degree': 3,
                  'tol': 0.001,
                  'C': 1.0,
                  'sliding_window': 288
                  }
        """dict: Dictionary of Hyperparameter configuration of the model"""
        self.parameter_list = {'kernel': ('linear', 'poly', 'rbf', 'sigmoid'),
                               'degree': [2, 3, 4, 5, 6, 7, 8, 9, 10],
                               }
        """dict: Dictionary of hyperparameters search space"""
        self.sliding_window = 0
        """int: sliding window to apply in the training phase"""

        self.__history_X = None
        """np.array: temporary training features"""
        self.__history_y = None
        """np.array: temporary training labels"""

        # Model configuration
        self.verbose = True
        """Boolean: Print output of the training phase"""

    def create_model(self):
        """
        Create an instance of the model. This function contains the definition and the library of the model
        :return: None
        """
        self.model = svm.SVR(kernel=self.p['kernel'],
                             degree=self.p['degree'])

    def fit(self):
        """
        Training of the model
        :return: None
        """
        self.ds.X_train_array = self.ds.X_train[:, :, 0]
        self.ds.y_train_array = self.ds.y_train.reshape(-1, 1)
        self.ds.X_test_array = self.ds.X_test[:, :, 0]
        self.ds.y_test_array = self.ds.y_test.reshape(-1, 1)

        self.__history_X = self.ds.X_train_array
        self.__history_y = self.ds.y_train_array

        self.model = self.model.fit(self.__history_X, self.__history_y)

    def predict(self, X):
        """
        Inference step on the samples X
        :param X: np.array: Input samples to predict
        :return: np.array: predictions: Predictions of the samples X
        """
        if self.model is None:
            print("ERROR: the model needs to be trained before predict")
            return

        if self.model is None:
            print("ERROR: the model needs to be trained before predict")
            return

        predictions = self.model.predict(X)

        return predictions

    def hyperparametrization(self):
        """
        Search the best parameter configuration
        :return: None
        """
        self.ds.X_train_array = self.ds.X_train[:, :, 0]
        self.ds.y_train_array = self.ds.y_train.reshape(-1, 1)
        self.ds.X_test_array = self.ds.X_test[:, :, 0]
        self.ds.y_test_array = self.ds.y_test.reshape(-1, 1)

        self.__temp_model = svm.SVR()
        tscv = TimeSeriesSplit(n_splits=10)
        mse_score = make_scorer(mean_squared_error, greater_is_better=False)

        svr_gs = GridSearchCV(estimator=self.__temp_model, cv=tscv, param_grid=self.parameter_list, scoring=mse_score,
                              verbose=self.verbose)
        svr_gs.fit(self.ds.X_train[:, :, 0], self.ds.y_train.reshape(-1, 1))
        df = pd.DataFrame(svr_gs.cv_results_)
        df.to_csv("talos/" + self.name + ".csv")

        print("BEST MODEL", svr_gs.best_estimator_)
        print("BEST PARAMS", svr_gs.best_params_)
        print("BEST SCORE", svr_gs.best_score_)

        self.p['kernel'] = svr_gs.best_params_['kernel']
        self.p['degree'] = svr_gs.best_params_['degree']
