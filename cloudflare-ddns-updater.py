#!/usr/bin/env python3

# Periodically checks the WAN IP address of this device by calling myip.dnsomatic.com and submit the change to the provided Cloudflare zone and DNS record, if necessary.
#
# by James Margatan

import argparse
import datetime
import errno
import json
import logging
import logging.handlers
import os
import random
import requests
import time

MINUTE_IN_SECONDS = 60

# Const for app args.
ARG_ZONE_ID = 'zone_id'
ARG_DNS_RECORD_ID = 'dns_record_id'
ARG_EMAIL = 'email'
ARG_KEY = 'key'

# Const for Cloudflare request headers.
CF_HEADER_EMAIL = 'X-Auth-Email'
CF_HEADER_KEY = 'X-Auth-Key'

CF_DNS_RECORD_IP_FIELD = 'content'

CF_ZONE_AND_DNS_RECORD_URL_TEMPLATE = 'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}'

CF_URL_EXAMPLE = CF_ZONE_AND_DNS_RECORD_URL_TEMPLATE.format(
  zone_id = ':' + ARG_ZONE_ID,
  dns_record_id = ':' + ARG_DNS_RECORD_ID)

DNS_O_MATIC_URL = 'http://myip.dnsomatic.com/'

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

def get_wan_ip():
  r = requests.get(DNS_O_MATIC_URL)
  try:
    r.raise_for_status()
    return r.text
  except Exception as e:
    raise RuntimeError('Unable to get WAN IP.') from e

def get_cloudflare_dns_record_url(zone_id, dns_record_id):
  return CF_ZONE_AND_DNS_RECORD_URL_TEMPLATE.format(
    zone_id = zone_id,
    dns_record_id = dns_record_id)

def get_cloudflare_dns_record_headers(email, key):
  return {
    CF_HEADER_EMAIL: email,
    CF_HEADER_KEY: key
  }

def get_cloudflare_dns_record(cfg):
  cf_url = get_cloudflare_dns_record_url(cfg.zone_id, cfg.dns_record_id)
  cf_headers = get_cloudflare_dns_record_headers(cfg.email, cfg.key)

  r = requests.get(cf_url, headers=cf_headers)
  try:
    r.raise_for_status()
    return r.json().get('result', {})
  except Exception as e:
    raise RuntimeError(f'Unable to get Cloudflare DNS record for [zone_id: {cfg.zone_id}] [dns_record_id: {cfg.dns_record_id}].') from e

def get_ip_from_dns_record(dns_record):
  ip_from_dns_record = dns_record.get(CF_DNS_RECORD_IP_FIELD)
  if not ip_from_dns_record:
    raise RuntimeError(f'Unable to get IP address from [dns_record: {dns_record}].')

  return ip_from_dns_record

class Config:
  def __init__(self, args):
    self.zone_id = args.zone_id
    self.dns_record_id = args.dns_record_id
    self.email = args.email
    self.key = args.key
    self.min_frequency = args.frequency[0]
    self.max_frequency = args.frequency[1]
    self.log_dir = args.log_dir

  def __str__(self):
    return f'config:\n\
      {ARG_ZONE_ID}: {self.zone_id}\n\
      {ARG_DNS_RECORD_ID}: {self.dns_record_id}\n\
      {ARG_EMAIL}: {self.email}\n\
      {ARG_KEY}: {self.key}\n\
      min_frequency: {self.min_frequency}\n\
      max_frequency: {self.max_frequency}\n\
      log_dir: {self.log_dir}'

def check_and_update(cfg):
  LOG.info('Initiating check and update...')
  wan_ip = get_wan_ip()
  dns_record = get_cloudflare_dns_record(cfg)
  ip_from_dns_record = get_ip_from_dns_record(dns_record)

  if wan_ip == ip_from_dns_record:
    LOG.info(f'No update needed. [wan_ip and ip_from_dns_record: {wan_ip}] match.')
    return

  LOG.info(f'[wan_ip: {wan_ip}] and [ip_from_dns_record: {ip_from_dns_record}] differ. Initiating update...')

  # Update DNS record with the WAN IP address.
  dns_record[CF_DNS_RECORD_IP_FIELD] = wan_ip

  update_cloudflare_dns_record(cfg, dns_record)

  LOG.info(f'Update successful.')
  return

def update_cloudflare_dns_record(cfg, dns_record):
  cf_url = get_cloudflare_dns_record_url(cfg.zone_id, cfg.dns_record_id)
  cf_headers = get_cloudflare_dns_record_headers(cfg.email, cfg.key)

  r = requests.put(cf_url, headers=cf_headers, data=json.dumps(dns_record))
  try:
    r.raise_for_status()
  except Exception as e:
    raise RuntimeError(f'Unable to update Cloudflare DNS record for [zone_id: {cfg.zone_id}] [dns_record_id: {cfg.dns_record_id}] with [dns_record: {dns_record}].') from e

def ensure_log_directory_exist(log_dir):
  if os.path.exists(log_dir):
    return

  try:
    os.makedirs(log_dir)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise RuntimeError(f'Unable to create [log_dir: {log_dir}].') from e

def main():
  arg_parser = argparse.ArgumentParser(description='Periodically checks the WAN IP address of this device by calling https://myip.dnsomatic.com/ and submit the change to the provided Cloudflare zone and DNS record, if necessary. Cloudflare API: ' + CF_URL_EXAMPLE)
  arg_parser.add_argument(ARG_ZONE_ID,
    help='The Cloudflare Zone ID where the DNS record to be modified belongs to.')
  arg_parser.add_argument(ARG_DNS_RECORD_ID,
    help='The Cloudflare DNS Record ID to be modified when the WAN IP of this device changes.')
  arg_parser.add_argument(ARG_EMAIL,
    help=f'The email address of a Cloudflare account that has access to the provided zone and DNS record. This information will be sent as the {CF_HEADER_EMAIL} header to the Cloudflare API.')
  arg_parser.add_argument(ARG_KEY,
    help=f'The API key of the Cloudflare account identified by the provided email address. This information will be sent as the {CF_HEADER_KEY} header to Cloudflare API.')
  arg_parser.add_argument('--frequency',
    nargs=2,
    default=[10, 10],
    metavar=('MIN', 'MAX'),
    type=int,
    help='The minimum and maximum duration (in minutes) on how frequent this script should be executed. The script is designed to randomly execute within the provided range to avoid a uniform pattern. If not set, by default, the script runs every 10 minutes.')
  arg_parser.add_argument('--log-dir',
    help='The directory where log files will be generated. The log is rotated every midnight and kept for 7 days. If not set, by default, it will log to console.')

  args = arg_parser.parse_args()
  cfg = Config(args)

  if cfg.log_dir is not None:
    ensure_log_directory_exist(cfg.log_dir)
    log_file_name = f'{cfg.log_dir}/cloudflare-dns-updater.out'
    log_handler = logging.handlers.TimedRotatingFileHandler(log_file_name,
      when='midnight',
      backupCount=7)
    log_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    log_handler.setLevel(logging.INFO)
    LOG.addHandler(log_handler)
    LOG.propagate = False
  else:
    logging.basicConfig(format=LOG_FORMAT)

  LOG.info(f'Starting Cloudflare DDNS Updater with {cfg}')

  while True:
    try:
      check_and_update(cfg)
    except Exception as e:
      LOG.exception(e)

    next_run_in_mins = random.randint(cfg.min_frequency, cfg.max_frequency)
    LOG.info(f'Script will be executed again in {next_run_in_mins} minute(s).')
    time.sleep(next_run_in_mins * MINUTE_IN_SECONDS)

# Execute the script.
main()
