"""Simula uploads de metadados para o Replica Set MongoDB.

Uso:
  python client/upload_sim.py [--count N] [--uri MONGO_URI]

O script conecta ao cluster (por padrão localhost:27017..27021), insere documentos de metadados
com writeConcern majority para garantir consistência forte.
"""

import argparse
import random
import time
from datetime import datetime, timezone
from pymongo import MongoClient, WriteConcern

# Seeds padrão (útil para demo local via docker-compose)
SEEDS = ["mongodb://localhost:27017",
         "mongodb://localhost:27018",
         "mongodb://localhost:27019",
         "mongodb://localhost:27020",
         "mongodb://localhost:27021"]

# String de conexão para os 5 notebooks na rede
REPLICA_URI = "mongodb://10.63.144.180:27017,10.63.144.236:27017,10.63.144.43:27017,10.63.144.241:27017,10.63.144.171:27017/uploadDB?replicaSet=rs0"

DB_NAME = 'uploadDB'
COLLECTION = 'files'


def make_client(uri: str = None):
    # Replica set name: rsUpload (para notebooks na rede)
    if uri:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    else:
        # Usa a URI do replica set dos notebooks
        client = MongoClient(REPLICA_URI, serverSelectionTimeoutMS=5000)
    return client


def random_tags():
    pool = ['natureza', 'pessoa', 'urbano', 'evento', 'paisagem', 'macro']
    return random.sample(pool, k=random.randint(1, 3))


def simulate_uploads(count: int, pause: float = 0.2, uri: str = None):
    client = make_client(uri)
    db = client.get_database(DB_NAME)
    coll = db.get_collection(COLLECTION).with_options(write_concern=WriteConcern(w='majority', wtimeout=5000))

    for i in range(count):
        ts = int(time.time() * 1000)
        doc = {
            'filename': f'image_{ts}_{i}.jpg',
            'user': f'user_{random.randint(1, 5)}',
            'storage_path': f's3://bucket/photos/{ts}_{i}.jpg',
            'status': 'uploaded',
            'tags': random_tags(),
            # timezone-aware UTC datetime
            'upload_date': datetime.now(timezone.utc)
        }
        result = coll.insert_one(doc)
        print(f'Inserido _id={result.inserted_id} (w=majority)')
        time.sleep(pause)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=5, help='Número de uploads simulados')
    parser.add_argument('--uri', type=str, default=None, help='MongoDB URI para conectar ao replicaset (ex: mongodb://user:pass@ip1:27017,ip2:27017/?replicaSet=rsUpload)')
    args = parser.parse_args()
    simulate_uploads(args.count, uri=args.uri)
