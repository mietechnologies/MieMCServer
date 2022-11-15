"""
This module is intended to handle all calls to the requests framework.

Methods
-------
get(url,saveTo)
    Downloads a file from a url to save to a specified location.
"""

import requests
from util.logger import log

def get(url: str, save_to: str) -> str:
    """
    Downloads a file to a specific location and returns the path to that
    downloaded file once finished.

    Parameters
    ----------
    url : str
        The web address where the file/data is located.
    saveTo: str
        The directory where the file/data should be saved locally.

    Returns
    -------
    str | None
        The path to where the download was saved or None if an error occured.
    """
    
    with requests.get(url, stream=True) as request:
        request.raise_for_status()

        with open(save_to, 'wb') as file:
            for chunk in request.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                else:
                    log('Error: Unable to download file!')
                    return None
        
        return save_to
