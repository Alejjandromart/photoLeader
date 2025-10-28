import builtins
import types
import pytest

# Import os.path to ensure relative imports work when running pytest from repo root
from client import upload_sim, read_sim


class FakeCollection:
    def __init__(self, docs):
        self._docs = docs
        self._cursor = None

    def with_options(self, write_concern=None):
        return self

    def insert_one(self, doc):
        # emulate insertion by appending a shallow copy and returning an object with inserted_id
        copy = dict(doc)
        copy['_id'] = len(self._docs) + 1
        self._docs.append(copy)
        return types.SimpleNamespace(inserted_id=copy['_id'])

    def find(self, query=None):
        query = query or {}
        if 'tags' in query:
            key = query['tags']
            self._cursor = [d for d in reversed(self._docs) if key in d.get('tags', [])]
        else:
            self._cursor = list(reversed(self._docs))
        return self

    def sort(self, field, direction):
        # for tests the data is already in reverse chronological order; implement a noop
        return self

    def limit(self, n):
        if self._cursor is None:
            self._cursor = list(reversed(self._docs))
        self._cursor = self._cursor[:n]
        return self

    def __iter__(self):
        if self._cursor is None:
            self._cursor = list(reversed(self._docs))
        return iter(self._cursor)


class FakeDB:
    def __init__(self, docs):
        self._docs = docs

    def get_collection(self, name):
        return FakeCollection(self._docs)


class FakeMongoClient:
    def __init__(self, *args, **kwargs):
        # shared in-memory docs list per client instance
        self._docs = []

    def get_database(self, name):
        return FakeDB(self._docs)


def test_simulate_uploads_inserts_documents(monkeypatch):
    fake_client = FakeMongoClient()

    # Patch the MongoClient used in upload_sim.make_client
    monkeypatch.setattr(upload_sim, 'MongoClient', lambda *args, **kwargs: fake_client)

    # Run a small number of uploads
    upload_sim.simulate_uploads(count=3, pause=0)

    # After inserts, check that the fake client's DB has 3 documents
    db = fake_client.get_database(upload_sim.DB_NAME)
    coll = db.get_collection(upload_sim.COLLECTION)
    docs = list(coll.find())
    assert len(docs) == 3
    for d in docs:
        assert d['status'] == 'uploaded'
        assert 'filename' in d
        assert 'user' in d


def test_list_gallery_filters_by_tag(monkeypatch, capsys):
    # Prepare fake client with some docs
    fake_client = FakeMongoClient()
    db = fake_client.get_database(read_sim.DB_NAME)
    coll = db.get_collection(read_sim.COLLECTION)

    # insert docs manually into the fake collection
    docs = [
        {'_id': 1, 'filename': 'a.jpg', 'user': 'u1', 'status': 'uploaded', 'tags': ['natureza'], 'upload_date': None},
        {'_id': 2, 'filename': 'b.jpg', 'user': 'u2', 'status': 'processed', 'tags': ['urbano'], 'upload_date': None},
        {'_id': 3, 'filename': 'c.jpg', 'user': 'u3', 'status': 'uploaded', 'tags': ['natureza', 'macro'], 'upload_date': None},
    ]
    # directly append to underlying docs storage
    fake_client._docs.extend(docs)

    # Patch the MongoClient used by read_sim
    monkeypatch.setattr(read_sim, 'MongoClient', lambda *args, **kwargs: fake_client)

    # Call list_gallery filtering by tag 'natureza'
    read_sim.list_gallery(tag='natureza', limit=10)

    captured = capsys.readouterr()
    output = captured.out.strip()
    # Expect two printed lines (for doc ids 3 and 1 in reverse chronological order)
    assert '_id=3' in output
    assert '_id=1' in output
    assert '_id=2' not in output
