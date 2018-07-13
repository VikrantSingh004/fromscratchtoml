#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Mohit Rathore <mrmohitrathoremr@gmail.com>
# Licensed under the GNU General Public License v3.0 - https://www.gnu.org/licenses/gpl-3.0.en.html

import numpy as np

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def mean_squared_error(y_predicted, y_target, return_deriv=False):
    """
    Calculates the mean square error between the predicted and the target ouputs.

    Parameters
    ----------
    y_predicted : numpy.ndarray
        The ouput predicted by the model.
    y_target : numpy.ndarray
        The expected output.
    return_deriv : bool, optional
        If set to true, the function returns derivative of the error along with the error.

    Returns
    -------
    numpy.array : The error.
    numpy.array : The error's derivative, optional.
    """
    if len(y_target.shape) == 1:
        y_target = np.expand_dims(y_target, axis=1)
    if return_deriv:
        return np.mean(np.square(y_predicted - y_target)), y_predicted - y_target
    return np.mean(np.square(y_predicted - y_target))

def cross_entropy(y_predicted, y_target, return_deriv=False):
    """
    Calculates the mean square error between the predicted and the target ouputs.

    Parameters
    ----------
    y_predicted : numpy.ndarray
        The ouput predicted by the model.
    y_target : numpy.ndarray
        The expected output.
    return_deriv : bool, optional
        If set to true, the function returns derivative of the error along with the error.

    Returns
    -------
    numpy.array : The error.
    numpy.array : The error's derivative, optional.
    """
    if len(y_target.shape) == 1:
        y_target = np.expand_dims(y_target, axis=1)

    y_predicted = np.clip(y_predicted, 1e-15, 1 - 1e-15)

    crl = -(y_target * np.log(y_predicted) + (1 - y_target) * np.log(1 - y_predicted))

    if return_deriv:
        deriv = -(y_target / y_predicted) + (1 - y_target) / (1 - y_predicted)
        return crl, deriv

    return crl