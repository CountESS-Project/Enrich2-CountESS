#  Copyright 2016-2017 Alan F Rubin, Daniel C Esposito
#
#  This file is part of Enrich2.
#
#  Enrich2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Enrich2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Enrich2. If not, see <http://www.gnu.org/licenses/>.


"""
Enrich2 statistics random_effects module
========================================

Module contains functions for the random effects model used for calculating
score statistics. See notes for references.
"""


import numpy as np


__all__ = [
    "rml_estimator",
    "nan_filter_generator",
]

def __old_rml_estimator(y, sigma2i, iterations=50):
    """
    Implementation of the robust maximum likelihood estimator.

    Parameters
    ----------
    y : :py:class:`~numpy.ndarray`, (n_replicates, n_variants)
        The variant scores matrix
    sigma2i : :py:class:`~numpy.ndarray`, (n_replicates, n_variants)
        The score variance matrix
    iterations : `int`
        Number of iterations to perform.
    
    Returns
    -------
    `tuple`
        Tuple of :py:class:`~numpy.ndarray` objects, corresponding to
        ``betaML``, ``sigma2ML``, ``eps``.

    Notes
    -----
    @book{demidenko2013mixed,
      title={Mixed models: theory and applications with R},
      author={Demidenko, Eugene},
      year={2013},
      publisher={John Wiley \& Sons}
    }

    """
    w = 1 / sigma2i
    sw = np.sum(w, axis=0)
    beta0 = np.sum(y * w, axis=0) / sw
    sigma2ML = np.sum((y - np.mean(y, axis=0)) ** 2 / (len(beta0) - 1), axis=0)
    eps = np.zeros(beta0.shape)
    for _ in range(iterations):
        w = 1 / (sigma2i + sigma2ML)
        sw = np.sum(w, axis=0)
        sw2 = np.sum(w ** 2, axis=0)
        betaML = np.sum(y * w, axis=0) / sw
        sigma2ML_new = sigma2ML * np.sum(((y - betaML) ** 2) * (w ** 2),
                                         axis=0) / (sw - (sw2 / sw))
        eps = np.abs(sigma2ML - sigma2ML_new)
        sigma2ML = sigma2ML_new
    return betaML, sigma2ML, eps


def nan_filter_generator(data):
    """
    Partition data based on the number of NaNs a column has, corresponding
    to the number of replicates a variant has across selections.

    Parameters
    ----------
    data : :py:class:`pd.ndarray`
        The numpy array to filter

    Returns
    -------
    `generator`
        A generator of tuples containing a filtered array along with 
        the number of replicates each row appears in
    """
    max_replicates = data.shape[0]
    data_num_nans = np.sum(np.isnan(data), axis=0)
    for k in range(0, max_replicates, 1):
        selector = data_num_nans == k
        if np.sum(selector) == 0:
            continue
        data_k = np.apply_along_axis(
            lambda col: col[~np.isnan(col)], 0, data[:, selector])
        rep_num = max_replicates - k
        yield data_k, rep_num


def rml_estimator(y, sigma2i, iterations=50):
    """
    Implementation of the robust maximum likelihood estimator.

    Parameters
    ----------
    y : :py:class:`~numpy.ndarray`, (n_replicates, n_variants)
        The variant scores matrix
    sigma2i : :py:class:`~numpy.ndarray`, (n_replicates, n_variants)
        The score variance matrix
    iterations : `int`
        Number of iterations to perform.
    
    Returns
    -------
    `tuple`
        Tuple of :py:class:`~numpy.ndarray` objects, corresponding to
        ``betaML``, ``sigma2ML``, ``eps``.

    Notes
    -----
    @book{demidenko2013mixed,
      title={Mixed models: theory and applications with R},
      author={Demidenko, Eugene},
      year={2013},
      publisher={John Wiley \& Sons}
    }
    
    """
    # Initialize each array to be have len number of variants
    max_replicates = y.shape[0]
    betaML = np.zeros(shape=(y.shape[1],)) * np.nan
    sigma2ML = np.zeros(shape=(y.shape[1],)) * np.nan
    eps = np.zeros(shape=(y.shape[1],)) * np.nan
    nreps = np.zeros(shape=(y.shape[1],)) * np.nan
    y_num_nans = np.sum(np.isnan(y), axis=0)
    for k in range(0, max_replicates, 1):
        # Partition y based on the number of NaNs a column has,
        # corresponding to the number of replicates a variant has
        # across selections.
        selector = y_num_nans == k
        if np.sum(selector) == 0:
            continue

        y_k = np.apply_along_axis(
            lambda col: col[~np.isnan(col)], 0, y[:, selector])
        sigma2i_k = np.apply_along_axis(
            lambda col: col[~np.isnan(col)], 0, sigma2i[:, selector])

        # Main alogrithm on the formatted data
        w_k = 1 / sigma2i_k
        sw_k = np.sum(w_k, axis=0)
        beta0_k = np.sum(y_k * w_k, axis=0) / sw_k
        sigma2ML_k = np.sum(
            (y_k - np.mean(y_k, axis=0)) ** 2 / (len(beta0_k) - 1), axis=0
        )
        eps_k = np.zeros(beta0_k.shape)
        for _ in range(iterations):
            w_k = 1 / (sigma2i_k + sigma2ML_k)
            sw_k = np.sum(w_k, axis=0)
            sw2_k = np.sum(w_k ** 2, axis=0)
            betaML_k = np.sum(y_k * w_k, axis=0) / sw_k

            num = np.sum(((y_k - betaML_k) ** 2) * (w_k ** 2),axis=0)
            denom = (sw_k - (sw2_k / sw_k))
            sigma2ML_k_new = sigma2ML_k * num / denom
            eps_k = np.abs(sigma2ML_k - sigma2ML_k_new)
            sigma2ML_k = sigma2ML_k_new

        # Handles the case when SE is 0 resulting in NaN values.
        betaML_k[np.isnan(betaML_k)] = 0.
        sigma2ML_k[np.isnan(sigma2ML_k)] = 0.
        eps_k[np.isnan(eps_k)] = 0.

        betaML[selector] = betaML_k
        sigma2ML[selector] = sigma2ML_k
        eps[selector] = eps_k
        nreps[selector] = max_replicates - k

    return betaML, sigma2ML, eps, nreps

