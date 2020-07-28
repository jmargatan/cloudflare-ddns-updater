Cloudflare Dynamic DNS (DDNS) Updater
===

Periodically checks the WAN IP address of this device by calling [a WAN IP echo server](https://ipinfo.io/ip) and submit the change to the provided Cloudflare zone and DNS record, if necessary.

Cloudflare API:
`https://api.cloudflare.com/client/v4/zones/:zone_id/dns_records/:dns_record_id`

```
$ ./cloudflare-ddns-updater.py -h
usage: cloudflare-ddns-updater.py [-h] [--frequency MIN MAX]
                                  [--log-dir LOG_DIR]
                                  zone_id dns_record_id api_token

Periodically checks the WAN IP address of this device by calling
a WAN IP echo server and submit the change to the provided Cloudflare
zone and DNS record, if necessary. Cloudflare API:
https://api.cloudflare.com/client/v4/zones/:zone_id/dns_records/:dns_record_id

positional arguments:
  zone_id              The Cloudflare Zone ID where the DNS record to be
                       modified belongs to.
  dns_record_id        The Cloudflare DNS Record ID to be modified when the
                       WAN IP of this device changes.
  api_token            The token of the API created by you to manipulate DNS
                       addresses. This information will be sent as the
                       Authorization header to Cloudflare API. If you don't
                       have one yet, go to your Cloudflare dashboard and
                       create an API token with the Edit zone DNS template to
                       get your token.

optional arguments:
  -h, --help           show this help message and exit
  --frequency MIN MAX  The minimum and maximum duration (in minutes) on how
                       frequent this script should be executed. The script is
                       designed to randomly execute within the provided range
                       to avoid a uniform pattern. If not set, by default, the
                       script runs every 10 minutes.
  --log-dir LOG_DIR    The directory where log files will be generated. The
                       log is rotated every midnight and kept for 7 days. If
                       not set, by default, it will log to console.
```

# Got issue?

The easiest way to run this is by using [pipenv](https://github.com/pypa/pipenv). The installation steps on MacOS (with [Homebrew](https://brew.sh/)) is roughly:
```
$ brew install pipenv

# Run this in the project directory, e.g. ~/cloudflare-ddns-updater/
$ pipenv install
```

To run:
```
# Run this in the project directory, e.g. ~/cloudflare-ddns-updater/
$ pipenv shell

# Inside the shell, run the script.
$ ./cloudflare-ddns-updater.py -h
```

by James Margatan
