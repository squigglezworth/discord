#!/bin/bash

# Example script showing how to download the IMDb dataset archives and import them to an sqlite db
# Seeding the db will take an hour or more
# Takes up 10-15GB (2x that if you use a tmp db as this script does, to reduce downtime)

wget -N -P "$@/imdb-dataset/" \
"https://datasets.imdbws.com/name.basics.tsv.gz" \
"https://datasets.imdbws.com/title.akas.tsv.gz" \
"https://datasets.imdbws.com/title.basics.tsv.gz" \
"https://datasets.imdbws.com/title.crew.tsv.gz" \
"https://datasets.imdbws.com/title.episode.tsv.gz" \
"https://datasets.imdbws.com/title.principals.tsv.gz" \
"https://datasets.imdbws.com/title.ratings.tsv.gz"

wget -N https://raw.githubusercontent.com/squigglezworth/cinemagoer/master/bin/s32cinemagoer.py \
&& \
python3 s32cinemagoer.py --verbose --cleanup "$@/imdb-dataset/" "sqlite:///$@/imdb.tmp.sqlite" \
&& \
mv "$@/imdb.tmp.sqlite" "$@/imdb.sqlite" \
&& \
ln -s "$@/imdb.sqlite" "imdb.sqlite" \
&& \
rm -rf "$@/imdb-dataset/"
