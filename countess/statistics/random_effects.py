"""
Enrich2 statistics random_effects module
========================================

Module contains functions for the random effects model used for calculating
score statistics. See notes for references.
"""


import numpy as np


__all__ = ["rml_estimator", "nan_filter_generator"]


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
        ``betaML``, ``var_betaML``, ``eps``.

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
        sigma2ML_new = (
            sigma2ML
            * np.sum(((y - betaML) ** 2) * (w ** 2), axis=0)
            / (sw - (sw2 / sw))
        )
        eps = np.abs(sigma2ML - sigma2ML_new)
        sigma2ML = sigma2ML_new

    var_betaML = 1 / np.sum(1 / (sigma2i + sigma2ML), axis=0)
    return betaML, var_betaML, eps


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
    for k in range(0, max_replicates - 1, 1):
        selector = data_num_nans == k
        if np.sum(selector) == 0:
            continue
        data_k = np.apply_along_axis(
            lambda col: col[~np.isnan(col)], 0, data[:, selector]
        )
        rep_num = max_replicates - k
        yield data_k, rep_num


def partitioned_rml_estimator(y, sigma2i, iterations=50):
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
        ``betaML``, ``var_betaML``, ``eps``.

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
    var_betaML = np.zeros(shape=(y.shape[1],)) * np.nan
    eps = np.zeros(shape=(y.shape[1],)) * np.nan
    nreps = np.zeros(shape=(y.shape[1],)) * np.nan
    y_num_nans = np.sum(np.isnan(y), axis=0)

    for k in range(0, max_replicates - 1, 1):
        # Partition y based on the number of NaNs a column has,
        # corresponding to the number of replicates a variant has
        # across selections.
        selector = y_num_nans == k
        if np.sum(selector) == 0:
            continue

        y_k = np.apply_along_axis(lambda col: col[~np.isnan(col)], 0, y[:, selector])
        sigma2i_k = np.apply_along_axis(
            lambda col: col[~np.isnan(col)], 0, sigma2i[:, selector]
        )

        betaML_k, var_betaML_k, eps_k = rml_estimator(y_k, sigma2i_k, iterations)

        # Handles the case when SE is 0 resulting in NaN values.
        betaML_k[np.isnan(betaML_k)] = 0.0
        var_betaML_k[np.isnan(var_betaML_k)] = 0.0
        eps_k[np.isnan(eps_k)] = 0.0

        betaML[selector] = betaML_k
        var_betaML[selector] = var_betaML_k
        eps[selector] = eps_k
        nreps[selector] = max_replicates - k

    return betaML, var_betaML, eps, nreps
