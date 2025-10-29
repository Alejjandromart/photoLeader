# Single Leader Pattern - MongoDB Replica Set

## O que é o Single Leader Pattern?

O **Single Leader Pattern** (também chamado de Primary-Backup ou Master-Slave) é um padrão de replicação onde:

- **UM único nó** é o líder (PRIMARY) e aceita todas as operações de **escrita**
- **Múltiplos nós secundários** (SECONDARY) replicam os dados do líder
- As **leituras** podem ser feitas de qualquer nó (PRIMARY ou SECONDARY)
- O líder tem **prioridade fixa**, sempre retoma sua posição quando volta online

## Arquitetura Implementada

```
┌─────────────────────────────────────────────────────────────┐
│                    SINGLE LEADER PATTERN                     │
└─────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────┐
        │   PRIMARY (Líder Principal)      │
        │   10.76.9.53:27017               │
        │   Prioridade: 5 ⭐⭐⭐⭐⭐        │
        │   - Aceita TODAS as escritas     │
        │   - Replica para secundários     │
        └─────────────┬────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ SECONDARY  │ │ SECONDARY  │ │ SECONDARY  │
│ Backup #1  │ │ Backup #2  │ │ Backup #3  │
│ 10.76.1.212│ │10.76.10.131│ │ 10.76.6.1  │
│ Prior: 3⭐⭐⭐│ │ Prior: 2⭐⭐│ │ Prior: 1⭐ │
└────────────┘ └────────────┘ └────────────┘
```

## Hierarquia de Prioridades

| Nó | IP | Prioridade | Papel |
|---|---|---|---|
| **mongo1** | 10.76.9.53 | ⭐⭐⭐⭐⭐ (5) | **LÍDER PRINCIPAL** - Sempre PRIMARY |
| **mongo2** | 10.76.1.212 | ⭐⭐⭐ (3) | **BACKUP PRIMÁRIO** - Assume se líder cair |
| **mongo3** | 10.76.10.131 | ⭐⭐ (2) | **BACKUP SECUNDÁRIO** - 3ª opção |
| **mongo4** | 10.76.1.61 | ⭐ (1) | **BACKUP TERCIÁRIO** - 4ª opção |
| **mongo5** | 10.76.6.1 | ⭐ (1) | **BACKUP TERCIÁRIO** - 5ª opção |

## Como Funciona a Eleição?

### Cenário 1: Sistema Normal
```
PRIMARY:   mongo1 (10.76.9.53) - Priority 5 ✅
SECONDARY: mongo2 (10.76.1.212) - Priority 3
SECONDARY: mongo3 (10.76.10.131) - Priority 2
SECONDARY: mongo4, mongo5 - Priority 1
```

### Cenário 2: Líder Principal Cai
```
❌ mongo1 CAI (10.76.9.53)

1. Heartbeats detectam falha (10 segundos)
2. Eleição é iniciada
3. mongo2 tem maior prioridade (3) entre disponíveis
4. mongo2 se torna o novo PRIMARY ✅

Resultado:
PRIMARY:   mongo2 (10.76.1.212) - Priority 3 ✅
SECONDARY: mongo3 (10.76.10.131) - Priority 2
SECONDARY: mongo4, mongo5 - Priority 1
```

### Cenário 3: Líder Principal Volta
```
✅ mongo1 VOLTA ONLINE (10.76.9.53)

1. mongo1 sincroniza dados com mongo2 (atual PRIMARY)
2. Após 30 segundos (catchUpTakeoverDelayMillis)
3. mongo1 força eleição (priority takeover)
4. mongo1 retoma posição de PRIMARY ✅

Resultado:
PRIMARY:   mongo1 (10.76.9.53) - Priority 5 ✅
SECONDARY: mongo2 (10.76.1.212) - Priority 3
SECONDARY: mongo3 (10.76.10.131) - Priority 2
SECONDARY: mongo4, mongo5 - Priority 1
```

### Cenário 4: Múltiplas Falhas
```
❌ mongo1 CAI
❌ mongo2 CAI

1. mongo3 tem maior prioridade (2) entre disponíveis
2. mongo3 se torna PRIMARY ✅

Se mongo1 OU mongo2 voltarem:
- Nó com maior prioridade retoma liderança
```

## Configurações do Padrão Single Leader

### catchUpTakeoverDelayMillis: 30000ms (30 segundos)
- **Por quê?** Quando o líder principal volta, ele precisa sincronizar dados
- **Como funciona:** Após sincronizar, aguarda 30s e força nova eleição
- **Resultado:** Líder original retoma seu lugar automaticamente

### Priority Takeover (Retomada por Prioridade)
```javascript
// Quando mongo1 (priority 5) volta online:
1. mongo1 detecta que NÃO é PRIMARY
2. mongo1 sincroniza dados com PRIMARY atual
3. Após 30 segundos, mongo1 inicia "priority takeover"
4. Nova eleição: mongo1 vence por ter maior prioridade
5. mongo1 volta a ser PRIMARY
```

### Vantagens do Single Leader Pattern

✅ **Consistência**: Um único ponto de escrita evita conflitos
✅ **Simplicidade**: Fácil de entender e depurar
✅ **Previsibilidade**: Sempre sabemos qual nó será o líder
✅ **Recuperação Automática**: Líder principal retoma posição automaticamente
✅ **Failover Ordenado**: Sucessão clara em caso de múltiplas falhas

### Desvantagens

⚠️ **Single Point of Failure**: Escritas param se líder cair (até novo líder ser eleito)
⚠️ **Latência em Escrita**: Todas escritas vão para um único nó
⚠️ **Escalabilidade Limitada**: Escritas não escalam horizontalmente

## Comandos Úteis

### Ver hierarquia atual
```bash
docker exec -it mongo1 mongosh --eval "rs.status().members.map(m => ({name: m.name, state: m.stateStr, priority: rs.conf().members.find(cfg => cfg.host === m.name).priority})).sort((a,b) => b.priority - a.priority)"
```

### Forçar mongo1 a retomar liderança (se não for PRIMARY)
```bash
docker exec -it mongo1 mongosh --eval "rs.stepDown(0, 1)"
```

### Testar failover (derrubar líder atual)
```bash
# Ver qual é o PRIMARY
docker exec -it mongo1 mongosh --eval "rs.status().members.filter(m => m.stateStr === 'PRIMARY')[0].name"

# Se for mongo1, derrubá-lo
docker stop mongo1

# Aguardar ~15 segundos e ver novo líder
docker exec -it mongo3 mongosh --eval "rs.status().members.filter(m => m.stateStr === 'PRIMARY')"

# Restaurar mongo1
docker start mongo1

# Aguardar ~45 segundos e mongo1 retoma liderança
```

### Alterar prioridades
```javascript
cfg = rs.conf();
cfg.members[0].priority = 10;  // mongo1 prioridade MÁXIMA
cfg.members[1].priority = 5;   // mongo2 backup primário
rs.reconfig(cfg);
```

## Monitoramento

### Verificar se líder correto está ativo
```bash
docker exec -it mongo1 mongosh --eval "
var status = rs.status();
var primary = status.members.find(m => m.stateStr === 'PRIMARY');
var expectedPrimary = '10.76.9.53:27017';
if (primary.name === expectedPrimary) {
  print('✅ Líder correto: ' + primary.name);
} else {
  print('⚠️ Líder atual: ' + primary.name + ' (esperado: ' + expectedPrimary + ')');
}
"
```

## Resumo

O **Single Leader Pattern** implementado garante:

1. ✅ **mongo1 (10.76.9.53)** é SEMPRE o líder preferencial
2. ✅ **Failover automático** para backup em caso de falha
3. ✅ **Recuperação automática** - líder retoma posição ao voltar
4. ✅ **Hierarquia clara** de sucessão em caso de múltiplas falhas
5. ✅ **Consistência forte** - todas escritas em um único líder

Este é o padrão ideal para aplicações que priorizam **consistência** e **previsibilidade** sobre escalabilidade de escritas.
