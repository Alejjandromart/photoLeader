"""
API REST para o PhotoLeader - Backend
Conecta o frontend HTML/JS com o MongoDB Replica Set

Endpoints:
- GET /api/photos - Lista todas as fotos
- GET /api/photos/<id> - Busca uma foto específica
- POST /api/photos - Upload de metadados de foto
- DELETE /api/photos/<id> - Remove uma foto
- GET /api/photos/user/<username> - Fotos de um usuário
- GET /api/photos/tag/<tag> - Fotos por tag
- GET /api/stats - Estatísticas do sistema
- GET /api/health - Status da API e MongoDB
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Configuração do MongoDB
REPLICA_URI = os.environ.get(
    'MONGO_URI',
    "mongodb://admin:admin123@10.76.9.53:27017,10.76.1.212:27017,10.76.10.131:27017,10.76.6.1:27017,10.76.1.612:27017/uploadDB?replicaSet=rsUpload"
)

DB_NAME = 'uploadDB'
COLLECTION = 'files'

# Cliente MongoDB
try:
    client = MongoClient(REPLICA_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db[COLLECTION]
    print("✅ Conectado ao MongoDB Replica Set")
except Exception as e:
    print(f"❌ Erro ao conectar ao MongoDB: {e}")


# Helper para converter ObjectId em string
def serialize_doc(doc):
    """Converte ObjectId para string para JSON"""
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc


# ============= ROTAS DA API =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica status da API e conexão com MongoDB"""
    try:
        # Ping no MongoDB
        client.admin.command('ping')
        
        # Status do Replica Set
        status = client.admin.command('replSetGetStatus')
        primary = None
        secondaries = []
        
        for member in status['members']:
            if member['stateStr'] == 'PRIMARY':
                primary = member['name']
            elif member['stateStr'] == 'SECONDARY':
                secondaries.append(member['name'])
        
        return jsonify({
            'status': 'healthy',
            'database': DB_NAME,
            'replica_set': status['set'],
            'primary': primary,
            'secondaries': secondaries,
            'members_count': len(status['members'])
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/photos', methods=['GET'])
def get_photos():
    """Lista todas as fotos (últimas 50)"""
    try:
        # Parâmetros de query
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        tag = request.args.get('tag')
        user = request.args.get('user')
        
        # Construir query
        query = {}
        if tag:
            query['tags'] = tag
        if user:
            query['user'] = user
        
        # Buscar documentos
        photos = list(collection.find(query)
                     .sort('upload_date', -1)
                     .skip(skip)
                     .limit(limit))
        
        # Serializar
        photos = [serialize_doc(p) for p in photos]
        
        return jsonify({
            'success': True,
            'count': len(photos),
            'photos': photos
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/photos/<photo_id>', methods=['GET'])
def get_photo(photo_id):
    """Busca uma foto específica por ID"""
    try:
        photo = collection.find_one({'_id': ObjectId(photo_id)})
        
        if not photo:
            return jsonify({
                'success': False,
                'error': 'Foto não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'photo': serialize_doc(photo)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/photos', methods=['POST'])
def upload_photo():
    """Cria metadados de uma nova foto"""
    try:
        data = request.get_json()
        
        # Validação básica
        if not data.get('filename'):
            return jsonify({
                'success': False,
                'error': 'Campo "filename" é obrigatório'
            }), 400
        
        if not data.get('user'):
            return jsonify({
                'success': False,
                'error': 'Campo "user" é obrigatório'
            }), 400
        
        # Criar documento
        photo = {
            'filename': data['filename'],
            'user': data['user'],
            'tags': data.get('tags', []),
            'upload_date': datetime.utcnow(),
            'status': data.get('status', 'uploaded'),
            'size_kb': data.get('size_kb', 0),
            'description': data.get('description', '')
        }
        
        # Inserir com writeConcern majority
        result = collection.with_options(
            write_concern={'w': 'majority'}
        ).insert_one(photo)
        
        return jsonify({
            'success': True,
            'photo_id': str(result.inserted_id),
            'message': 'Foto criada com sucesso'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/photos/<photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    """Remove uma foto"""
    try:
        result = collection.delete_one({'_id': ObjectId(photo_id)})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'error': 'Foto não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Foto removida com sucesso'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/photos/user/<username>', methods=['GET'])
def get_photos_by_user(username):
    """Lista fotos de um usuário específico"""
    try:
        photos = list(collection.find({'user': username})
                     .sort('upload_date', -1)
                     .limit(100))
        
        photos = [serialize_doc(p) for p in photos]
        
        return jsonify({
            'success': True,
            'user': username,
            'count': len(photos),
            'photos': photos
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/photos/tag/<tag>', methods=['GET'])
def get_photos_by_tag(tag):
    """Lista fotos por tag"""
    try:
        photos = list(collection.find({'tags': tag})
                     .sort('upload_date', -1)
                     .limit(100))
        
        photos = [serialize_doc(p) for p in photos]
        
        return jsonify({
            'success': True,
            'tag': tag,
            'count': len(photos),
            'photos': photos
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Estatísticas do sistema"""
    try:
        total_photos = collection.count_documents({})
        
        # Top usuários
        pipeline = [
            {'$group': {'_id': '$user', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        top_users = list(collection.aggregate(pipeline))
        
        # Top tags
        pipeline = [
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        top_tags = list(collection.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'total_photos': total_photos,
            'top_users': top_users,
            'top_tags': top_tags
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search', methods=['GET'])
def search_photos():
    """Busca fotos por texto no filename ou description"""
    try:
        query_text = request.args.get('q', '')
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Parâmetro "q" é obrigatório'
            }), 400
        
        # Busca com regex (case insensitive)
        photos = list(collection.find({
            '$or': [
                {'filename': {'$regex': query_text, '$options': 'i'}},
                {'description': {'$regex': query_text, '$options': 'i'}}
            ]
        }).limit(50))
        
        photos = [serialize_doc(p) for p in photos]
        
        return jsonify({
            'success': True,
            'query': query_text,
            'count': len(photos),
            'photos': photos
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Rota raiz
@app.route('/')
def index():
    """Página inicial da API"""
    return jsonify({
        'api': 'PhotoLeader API',
        'version': '1.0',
        'endpoints': {
            'health': '/api/health',
            'photos': '/api/photos',
            'upload': 'POST /api/photos',
            'delete': 'DELETE /api/photos/<id>',
            'user_photos': '/api/photos/user/<username>',
            'tag_photos': '/api/photos/tag/<tag>',
            'search': '/api/search?q=<query>',
            'stats': '/api/stats'
        }
    })


if __name__ == '__main__':
    print("🚀 Iniciando PhotoLeader API...")
    print(f"📊 Database: {DB_NAME}")
    print(f"📁 Collection: {COLLECTION}")
    print(f"🌐 Server: http://localhost:5000")
    print("\nEndpoints disponíveis:")
    print("  GET  /api/health          - Status da API")
    print("  GET  /api/photos          - Lista fotos")
    print("  POST /api/photos          - Upload de foto")
    print("  GET  /api/photos/<id>     - Busca foto")
    print("  DEL  /api/photos/<id>     - Remove foto")
    print("  GET  /api/photos/user/<u> - Fotos do usuário")
    print("  GET  /api/photos/tag/<t>  - Fotos por tag")
    print("  GET  /api/search?q=<text> - Busca texto")
    print("  GET  /api/stats           - Estatísticas")
    print("\n")
    
    # Run in non-debug mode for more stable background execution on Windows
    app.run(debug=False, host='0.0.0.0', port=5000)
