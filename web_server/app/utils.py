import csv
from pathlib import Path


def load_artists_mapping(csv_path):
    artists = {}
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            artists[int(row['Index'])] = row['Folder Name']
    return artists
