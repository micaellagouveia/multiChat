# Salas de Bate Papo

Construção de uma aplicação que disponibiliza salas de bate-papo virtuais, nas quais os clientes podem ingressar e interagir.

## Requisitos obrigatórios
- permitir a criação de salas virtuais com nome e limite de participantes;
- permitir a conexão de clientes, com um identificador, em uma sala existente;
- permitir a saída de clientes de uma sala em que estava participando;
- diálogo entre os clientes da sala.

Projeto realizado em Python, utilizando sockets.

## Como rodar o projeto

Não é necessário instalar nenhuma dependência, e para rodar o projeto

1. Rode primeiro o Servidor: ```python server.py```

O servidor estará rondando na porta ```5000```

2. Defina a quantidade máxima de clientes que o servidor irá aceitar

3. Rode os Clients em outros terminais: ```python client.py```
