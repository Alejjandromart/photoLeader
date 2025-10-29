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

from flask import Flask, jsonify, request, send_from_directory, send_file, Response
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId
from datetime import datetime
import gridfs
import io
import os
import traceback

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Configuração do MongoDB
REPLICA_URI = os.environ.get(
    'MONGO_URI',
    "mongodb://10.63.144.180:27017,10.63.144.236:27017,10.63.144.43:27017,10.63.144.241:27017,10.63.144.171:27017/uploadDB?replicaSet=rs0&readPreference=primary"
)

DB_NAME = 'uploadDB'
COLLECTION = 'files'

# Cliente MongoDB
try:
    from pymongo.read_preferences import ReadPreference
    from pymongo.write_concern import WriteConcern
    
    client = MongoClient(
        REPLICA_URI, 
        serverSelectionTimeoutMS=5000,
        readPreference='primary',  # Força leitura do PRIMARY
    )
    db = client[DB_NAME].with_options(
        write_concern=WriteConcern(w='majority', wtimeout=5000)
    )
    collection = db[COLLECTION]
    # GridFS será inicializado apenas quando necessário (lazy loading)
    fs = None
    print("✅ Conectado ao MongoDB Replica Set")
    print("✅ GridFS será inicializado on-demand")
except Exception as e:
    print(f"❌ Erro ao conectar ao MongoDB: {e}")


# Helper para obter GridFS (lazy initialization)
def get_gridfs():
    global fs
    if fs is None:
        # Criar índices GridFS manualmente para garantir que são criados no PRIMARY
        try:
            db.fs.chunks.create_index([("files_id", 1), ("n", 1)], unique=True)
            db.fs.files.create_index([("filename", 1), ("uploadDate", 1)])
            print("✅ Índices GridFS criados/verificados no PRIMARY")
        except Exception as e:
            print(f"⚠️ Aviso ao criar índices GridFS: {e}")
        
        fs = gridfs.GridFS(db)
    return fs


# Helper para converter ObjectId em string
def serialize_doc(doc):
    """Converte ObjectId para string para JSON"""
    if doc:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
        if 'gridfs_id' in doc and isinstance(doc['gridfs_id'], ObjectId):
            doc['gridfs_id'] = str(doc['gridfs_id'])
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
        print("📸 Recebendo requisição GET /api/photos")
        
        # Parâmetros de query
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        tag = request.args.get('tag')
        user = request.args.get('user')
        
        print(f"   Params: limit={limit}, skip={skip}, tag={tag}, user={user}")
        
        # Construir query
        query = {}
        if tag:
            query['tags'] = tag
        if user:
            query['user'] = user
        
        print(f"   Query: {query}")
        
        # Usar collection com leitura de secondary para listar fotos
        read_collection = collection.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
        
        print("   Executando find()...")
        # Buscar documentos
        photos = list(read_collection.find(query)
                     .sort('upload_date', -1)
                     .skip(skip)
                     .limit(limit))
        
        print(f"   ✅ Encontradas {len(photos)} fotos")
        
        # Serializar e adicionar URL da foto
        photos = [serialize_doc(p) for p in photos]
        
        # Adicionar URL para visualização da foto
        for photo in photos:
            if 'gridfs_id' in photo:
                photo['photo_url'] = f"/api/photos/{photo['_id']}/file"
        
        print(f"   ✅ Retornando {len(photos)} fotos serializadas")
        return jsonify({
            'success': True,
            'count': len(photos),
            'photos': photos
        }), 200
    except Exception as e:
        print(f"❌ Erro ao listar fotos: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
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
        }, 200)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/photos', methods=['POST'])
def upload_photo():
    """Upload de foto completa usando GridFS"""
    try:
        # Verificar se há arquivo na requisição
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nome do arquivo vazio'
            }), 400
        
        # Obter metadados do formulário
        user = request.form.get('user', 'usuario_padrao')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        
        # Ler o arquivo em memória
        file_data = file.read()
        
        # Salvar no GridFS com writeConcern majority
        file_id = get_gridfs().put(
            file_data,
            filename=file.filename,
            content_type=file.content_type,
            user=user,
            description=description,
            tags=tags,
            upload_date=datetime.utcnow(),
            size_kb=len(file_data) / 1024
        )
        
        # Criar documento de metadados na collection principal
        photo_doc = {
            'gridfs_id': file_id,
            'filename': file.filename,
            'user': user,
            'description': description,
            'tags': tags,
            'upload_date': datetime.utcnow(),
            'size_kb': len(file_data) / 1024,
            'content_type': file.content_type,
            'status': 'uploaded'
        }
        
        result = collection.insert_one(photo_doc)
        
        return jsonify({
            'success': True,
            'data': {
                '_id': str(result.inserted_id),
                'gridfs_id': str(file_id),
                'filename': file.filename,
                'user': user,
                'description': description,
                'tags': tags,
                'size_kb': round(len(file_data) / 1024, 2)
            },
            'message': 'Foto enviada com sucesso!'
        }), 201
        
    except Exception as e:
        print(f"Erro no upload: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/photos/<photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    """Remove uma foto e seu arquivo do GridFS"""
    try:
        # Buscar a foto para obter o gridfs_id
        photo = collection.find_one({'_id': ObjectId(photo_id)})
        
        if not photo:
            return jsonify({
                'success': False,
                'error': 'Foto não encontrada'
            }), 404
        
        # Remover arquivo do GridFS se existir
        if 'gridfs_id' in photo:
            try:
                get_gridfs().delete(photo['gridfs_id'])
            except Exception as e:
                print(f"Erro ao remover arquivo do GridFS: {e}")
        
        # Remover documento da collection
        collection.delete_one({'_id': ObjectId(photo_id)})
        
        return jsonify({
            'success': True,
            'message': 'Foto removida com sucesso'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/photos/<photo_id>/file', methods=['GET'])
def get_photo_file(photo_id):
    """Baixa o arquivo da foto do GridFS"""
    try:
        # Buscar a foto
        photo = collection.find_one({'_id': ObjectId(photo_id)})
        
        if not photo or 'gridfs_id' not in photo:
            return jsonify({
                'success': False,
                'error': 'Foto não encontrada'
            }), 404
        
        # Buscar arquivo no GridFS
        try:
            grid_out = get_gridfs().get(photo['gridfs_id'])
        except gridfs.errors.NoFile:
            return jsonify({
                'success': False,
                'error': 'Arquivo não encontrado no GridFS'
            }), 404
        
        # Retornar arquivo como resposta
        return Response(
            grid_out.read(),
            mimetype=photo.get('content_type', 'application/octet-stream'),
            headers={
                'Content-Disposition': f'inline; filename="{photo["filename"]}"'
            }
        )
        
    except Exception as e:
        print(f"Erro ao buscar arquivo: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
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


@app.route('/api/replicaset/status', methods=['GET'])
def get_replicaset_status():
    """Retorna o status detalhado dos membros do Replica Set"""
    print("📡 Requisição recebida em /api/replicaset/status")
    try:
        # Executar comando no PRIMARY usando direct_connection para evitar erro de routing
        # Tentar obter status usando qualquer membro disponível
        print("🔍 Tentando obter status do replica set...")
        try:
            status = client.admin.command('replSetGetStatus')
            print("✅ Status obtido com sucesso do cliente principal")
        except Exception as e:
            # Se falhar, tentar conectar diretamente no PRIMARY conhecido
            print(f"⚠️ Aviso ao obter status: {e}")
            print("🔄 Tentando conexão direta com o PRIMARY...")
            # Criar cliente temporário direto para admin commands
            temp_client = MongoClient(
                "mongodb://10.63.144.180:27017/?directConnection=true",
                serverSelectionTimeoutMS=5000
            )
            status = temp_client.admin.command('replSetGetStatus')
            temp_client.close()
            print("✅ Status obtido via conexão direta")
        
        members = []
        for member in status.get('members', []):
            members.append({
                'name': member.get('name'),
                'state': member.get('stateStr'),
                'health': 'Healthy' if member.get('health') == 1 else 'Unhealthy',
                'uptime': member.get('uptime'),
                'pingMs': member.get('pingMs', 'N/A')
            })
        
        print(f"📊 Retornando dados de {len(members)} membros")
        return jsonify({
            'success': True,
            'replica_set_name': status.get('set'),
            'members': members
        }), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"❌ Erro no endpoint /api/replicaset/status: {str(e)}")
        print(f"📋 Traceback: {error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500


@app.route('/<path:path>')
def serve_static_files(path):
    """Serve arquivos estáticos do diretório frontend"""
    return send_from_directory('../frontend', path)


# Rota raiz
@app.route('/')
def index():
    """Serve a página de login como página inicial"""
    response = send_from_directory('../frontend', 'login.html')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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
    print("  GET  /api/replicaset/status - Status do Replica Set")
    print("\n")
    
    # Run in non-debug mode for stable Windows execution
    app.run(debug=False, host='0.0.0.0', port=5000)
