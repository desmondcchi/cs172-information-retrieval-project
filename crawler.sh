#!/bin/bash

# Usage: ./crawler.sh <seed_file.txt> <num_pages> <hops_away> <output_dir_name>

scrapy crawl web_crawler -a SEED_FILE_NAME="$1" -a NUM_PAGES=$2 -a HOPS_AWAY=$3 -a OUTPUT_DIR_NAME="$4"
