"""Simula leituras da galeria usando readPreference para Secondaries.

Uso:
  python client/read_sim.py [--tag TAG] [--uri MONGO_URI]

Este script conecta-se ao cluster com readPreference=secondaryPreferred para demonstrar
escala de leitura em followers. Pode receber uma URI completa via --uri.
"""

import argparse
from pymongo import MongoClient

SEEDS = ["mongodb://localhost:27017",
         "mongodb://localhost:27018",
         "mongodb://localhost:27019",
         "mongodb://localhost:27020",
         "mongodb://localhost:27021"]

DB_NAME = 'photoLeader'
COLLECTION = 'uploads'


def make_read_client(uri: str = None):
    # Conecta com preferência por secondaries para leituras escaláveis
    if uri:
        client = MongoClient(uri, replicaset='rs0', serverSelectionTimeoutMS=5000, readPreference='secondaryPreferred')
    else:
        client = MongoClient(SEEDS, replicaset='rs0', serverSelectionTimeoutMS=5000, readPreference='secondaryPreferred')
    return client


def list_gallery(tag: str = None, limit: int = 20, uri: str = None):
    client = make_read_client(uri)
    db = client.get_database(DB_NAME)
    coll = db.get_collection(COLLECTION)

    query = {}
    if tag:
        query['tags'] = tag

    docs = coll.find(query).sort('upload_date', -1).limit(limit)
    for d in docs:
        print(f"_id={d.get('_id')} user={d.get('user')} status={d.get('status')} tags={d.get('tags')} filename={d.get('filename')}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', type=str, help='Filtrar por tag')
    parser.add_argument('--uri', type=str, default=None, help='MongoDB URI para conectar ao replicaset')
    args = parser.parse_args()
    list_gallery(args.tag, uri=args.uri)
