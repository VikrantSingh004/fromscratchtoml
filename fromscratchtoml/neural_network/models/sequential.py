#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Mohit Rathore <mrmohitrathoremr@gmail.com>
# Licensed under the GNU General Public License v3.0 - https://www.gnu.org/licenses/gpl-3.0.en.html

from __future__ import print_function
import numpy as np

from fromscratchtoml.toolbox import progress, binary_visualize
from .. import losses

from fromscratchtoml.base import BaseModel

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Sequential(BaseModel):
    """
    A sequence of multiple layers.

    Examples
    --------
    >>> from fromscratchtoml.neural_network.models import Sequential
    >>> from fromscratchtoml.neural_network.optimizers import StochasticGradientDescent
    >>> from fromscratchtoml.neural_network.layers import Dense, Activation
    >>> X1 = np.array([[0, 0],[0, 1],[1, 0], [1, 1]])
    >>> y1 = np.array([[1,0], [0,1], [0,1], [1,0]])
    >>> model = Sequential()
    >>> model.add(Dense(5, input_dim=2, seed=1))
    >>> model.add(Activation('sigmoid'))
    >>> model.add(Dense(5, seed=2))
    >>> model.add(Activation('sigmoid'))
    >>> model.add(Dense(2, seed=3))
    >>> sgd = StochasticGradientDescent(learning_rate=0.1)
    >>> model.compile(optimizer=sgd, loss="mean_squared_error")
    >>> model.fit(X1, y1, batch_size=4, epochs=100)
    >>> model.predict(X1)
    """
    def __init__(self, verbose=False, vis_each_epoch=False):
        """
        Initialising the model parameters.

        Parameters
        ----------
        verbose : bool, optional
            If True, it will ouput the model state at each epoch.
        vis_each_epoch : bool, optional
            If True, and verbose is True - A visualisation of data along with model contours will be displayed at each
            epoch.
        """
        self.layers = []
        self.verbose = verbose
        self.vis_each_epoch = vis_each_epoch

    def compile(self, optimizer, loss):
        """
        Sets the optimizer and loss function to be used by the model.

        Parameters
        ----------
        optimizer : fromscratchtoml.neural_network.optimizers
            The procedure to be used for updating the weights.
        loss : string
            The loss function to be used.
        """
        self.optimizer = optimizer
        self.loss = getattr(losses, loss)

    def accuracy(self, X, y):
        """
        Calculates the model accuracy based on the current parameters.

        Parameters
        ----------
        X : numpy.ndarray
            The input to the model.
        y : numpy.ndarray
            The corresponding label to the input.

        Returns
        -------
        float : The accuracy in percentage.
        """

        if len(y.shape) > 1:
            y = np.argmax(y, axis=1)
        y_pred = self.predict(X)

        diff_arr = y - y_pred
        total_samples = y.shape[0]

        errors = np.count_nonzero(diff_arr) / 2
        return (100 - (errors / (total_samples * 0.01)))

    def fit(self, X, y, epochs, batch_size=None):
        """
        Fits the model.

        Parameters
        ----------
        X : numpy.ndarray
            The input to the model.
        y : numpy.ndarray
            The corresponding label to the input.
        epochs : int
            The number of complete passes over the entire data.
        batch_size : int, optional
            The number of data points to be processed in a single iteration.
        """
        if batch_size is None:
            batch_size = X.shape[0]

        for epoch in progress(range(epochs)):
            for current_batch in range(0, X.shape[0], batch_size):
                batch_X = X[current_batch: current_batch + batch_size]
                batch_y = y[current_batch: current_batch + batch_size]
                self.__update_batch(batch_X, batch_y)

            if self.verbose or epoch == epochs - 1:
                y_pred = self.predict(X, prob=True)
                loss = self.loss(y_pred, y)
                acc = self.accuracy(X, y)
                print("\nepoch: {}/{} ".format(epoch + 1, epochs), end="")
                print(" acc: {:0.2f} ".format(acc), end="")
                print(" loss: {:0.3f} ".format(loss))
                if self.vis_each_epoch:
                    binary_visualize(X, clf=self, draw_contour=True)

    def __update_batch(self, X, Y):
        """
        Optimizes the parameters of the model by processing the inputs in a batch.

        Parameters
        ----------
        X : numpy.ndarray
            The input to the model.
        Y : numpy.ndarray
            The corresponding label to the input.
        """
        y_pred = self.forwardpass(X)

        _, dEdO = self.loss(y_pred, Y, return_deriv=True)

        self.back_propogate_and_update(dEdO, self.optimizer)

    def back_propogate_and_update(self, dEdO, optimizer):
        """
        Backpropogate the error from the last layer to the first and then optimize the weights.

        Parameters
        ----------
        dEdO : numpy.ndarray
            The accumulated delta used for calculating error gradient with respect to parameters.
        optimizer : fromscratchtoml.neural_network.optimizers
            The optimizing procedure followed for updating the weights.
        """

        for layer in reversed(self.layers):
            dEdO = layer.back_propogate(dEdO)
            layer.optimize(optimizer)

    def forwardpass(self, X, return_deriv=False):
        """
        Forward pass the input through all the layers in the current model.

        Parameters
        ----------
        X : numpy.ndarray
            The input to the model.
        return_deriv : bool, optional
            If set to true, the function returns derivative of the output along with the output.

        Returns
        -------
        numpy.array : The output of the model.
        """
        Z = X

        for layer in self.layers:
            Z, Z_deriv = layer.forward(Z, return_deriv=True)

        if return_deriv:
            return Z, Z_deriv

        return Z

    def predict(self, X, prob=False):
        """
        Predicts the ouput of the model based on the trained parameters.

        Parameters
        ----------
        X : numpy.ndarray
            The input to be predicted.
        prob : bool, optional
            If set to true, it returns output probabilities of each class.

        Returns
        -------
        numpy.array : The prediction.
        """
        predictions = self.forwardpass(X)

        if prob is False:
            predictions = np.argmax(predictions, axis=1)

        return predictions

    def add(self, layer):
        """
        Adds the layer into the sequence.

        Parameters
        ----------
        layer : fromscratchtoml.neural_network.layers
            The layer to be added.
        """
        self.layers.append(layer)
