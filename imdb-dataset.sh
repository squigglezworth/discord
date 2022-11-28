#!/bin/bash

# This script downloads the IMDb dataset archives and imports them to imdb.sqlite
# Note: This process takes up 10-15GB and will take a while

wget -N -P /tmp/imdb-datasets/ \
"https://datasets.imdbws.com/name.basics.tsv.gz" \
"https://datasets.imdbws.com/title.akas.tsv.gz" \
"https://datasets.imdbws.com/title.basics.tsv.gz" \
"https://datasets.imdbws.com/title.crew.tsv.gz" \
"https://datasets.imdbws.com/title.episode.tsv.gz" \
"https://datasets.imdbws.com/title.principals.tsv.gz" \
"https://datasets.imdbws.com/title.ratings.tsv.gz"

wget -N https://raw.githubusercontent.com/cinemagoer/cinemagoer/master/bin/s32cinemagoer.py

s32cinemagoer.py /tmp/imdb-datasets/ sqlite:///imdb.sqlite
