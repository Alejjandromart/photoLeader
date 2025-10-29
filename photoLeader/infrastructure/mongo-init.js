// Arquivo de inicialização do Replica Set rs0 com 5 membros

config = {
  _id: "rs0",
  members: [
    { _id: 0, host: "192.168.0.3:27017" },//principal loq (esta máquina)
    { _id: 1, host: "192.168.0.8:27017" },//Ale
    { _id: 2, host: "10.76.10.131:27017" },//Aila
    { _id: 3, host: "10.76.1.61:27017" },//joel
    { _id: 4, host: "192.168.0.2:27017" }//legion
  ]
};

printjson(rs.initiate(config));

// Espera até que haja um PRIMARY
function waitForPrimary() {
  for (var i = 0; i < 30; i++) {
    try {
      var status = rs.status();
      if (status.ok && status.members) {
        for (var j = 0; j < status.members.length; j++) {
          if (status.members[j].stateStr === 'PRIMARY') {
            print('Primary elected: ' + status.members[j].name);
            return;
          }
        }
      }
    } catch (e) {}
    print('Aguardando eleição do Primary... ' + i);
    sleep(1000);
  }
  print('Timeout esperando Primary');
}

waitForPrimary();

print('Replica set rs0 iniciado.');

// Criar banco de dados e índices para a aplicação (upload metadata)
try {
  // usar o banco uploadDB
  var appDB = db.getSiblingDB('uploadDB');
  // cria coleção 'files' se não existir
  if (!appDB.getCollectionNames().includes('files')) {
    appDB.createCollection('files');
    print('Criada collection uploadDB.files');
  } else {
    print('Collection uploadDB.files já existe');
  }

  // criar índices úteis
  appDB.files.createIndex({ upload_date: -1 });
  appDB.files.createIndex({ user: 1 });
  appDB.files.createIndex({ tags: 1 });
  print('Índices criados em uploadDB.files (upload_date, user, tags)');
} catch (e) {
  print('Erro ao criar DB/índices: ' + e);
}
