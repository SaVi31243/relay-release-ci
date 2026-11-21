import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def check(base, path, expected):
    try:
        with urlopen(base + path, timeout=3.5) as response:
            status, body = response.status, response.read().decode()
    except HTTPError as error:
        with error:
            status, body = error.code, error.read().decode()
    except (URLError, OSError) as error:
        print(f"GET {path}: {error}")
        return False

    print(f"GET {path}: HTTP {status} {body.strip()}")
    try:
        return status == 200 and json.loads(body) == expected
    except ValueError:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("revision")
    args = parser.parse_args()

    base = f"http://127.0.0.1:{args.port}"
    health = check(base, "/health", {"mode": "serving"})
    version = check(base, "/version", {"revision": args.revision})
    raise SystemExit(0 if health and version else 1)
