#!/bin/bash
# Usage: ./crawler.sh <seed_file.txt> <allowed_domains.txt> <num_pages> <hops_away> <json_name>

scrapy crawl web_crawler -a SEED_FILE_NAME=$1 -a ALLOWED_DOMAINS_FILE_NAME=$2 -a MAX_NUM_PAGES=$3 -a MAX_HOPS_AWAY=$4 -o $5
