Cloudflare Dynamic DNS (DDNS) Updater
===

Periodically checks the WAN IP address of this device by calling [myip.dnsomatic.com](http://myip.dnsomatic.com/) and submit the change to the provided Cloudflare zone and DNS record, if necessary.

Cloudflare API:
`https://api.cloudflare.com/client/v4/zones/:zone_id/dns_records/:dns_record_id`

```
$ python3 cloudflare-ddns-updater.py -h
usage: cloudflare-ddns-updater.py [-h] [--frequency min max]
                                  zone_id dns_record_id email key

Periodically checks the WAN IP address of this device by calling
https://myip.dnsomatic.com/ and submit the change to the provided Cloudflare
zone and DNS record, if necessary. Cloudflare API:
https://api.cloudflare.com/client/v4/zones/:zone_id/dns_records/:dns_record_id

positional arguments:
  zone_id              The Cloudflare Zone ID where the DNS record to be
                       modified belongs to.
  dns_record_id        The Cloudflare DNS Record ID to be modified when the
                       WAN IP of this device changes.
  email                The email address of a Cloudflare account that has
                       access to the provided zone and DNS record. This
                       information will be sent as the X-Auth-Email header to
                       the Cloudflare API.
  key                  The API key of the Cloudflare account identified by the
                       provided email address. This information will be sent
                       as the X-Auth-Key header to Cloudflare API.

optional arguments:
  -h, --help           show this help message and exit
  --frequency min max  The minimum and maximum duration (in minutes) on how
                       frequent this script should be executed. The script is
                       designed to randomly execute within the provided range
                       to avoid a uniform pattern. If not set, by default, the
                       script runs every 10 minutes.
```

by James Margatan
