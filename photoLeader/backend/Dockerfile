# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo de dependências e instalar
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do backend
COPY . .

# Expor a porta que o Flask usa
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "api.py"]
