import requests
import uuid


def get_ipaddress(timeout=5):
    """
    Returns the public IP address of the server.

    Args:
        timeout (int): request timeout in seconds

    Returns:
        str: IP address if successful
        None: if failed
    """

    services = [
        "https://api.ipify.org",
        "https://ipinfo.io/ip",
        "https://ifconfig.me/ip"
    ]

    for url in services:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raises error for bad status codes

            ip = response.text.strip()

            if ip:
                return ip

        except requests.exceptions.Timeout:
            print(f"Timeout when connecting to {url}")

        except requests.exceptions.ConnectionError:
            print(f"Connection error when connecting to {url}")

        except requests.exceptions.HTTPError:
            print(f"HTTP error from {url}")

        except Exception as e:
            print(f"Unexpected error from {url}: {e}")

    return None

# generate unique txt referrence
