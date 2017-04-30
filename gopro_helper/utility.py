
import requests


def get(url, timeout=5):
    """Handy helper to GET information from URL
    """
    try:
        resp = requests.get(url, timeout=timeout)

        if resp.status_code != 200:
            print(resp.reason)
            print(resp.status_code)
            msg = 'Problem making request for: {}'.format(url)

            raise requests.RequestException(msg)
            # content = resp.json()
            # return content

        return resp.json()
    except requests.ConnectTimeout:
        print('timeout')

    # Done

