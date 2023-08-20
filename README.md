# SlimAPI - Rinha de Backend 2023

Para saber mais: https://github.com/zanfranceschi/rinha-de-backend-2023-q3

> Atenção! Algumas "técnicas" (gambiarras) foram usadas neste projeto para melhorar o tempo de resposta das requests, favor não repetir em casa. Não apenas "técnicas" mas também configurações. ESTEJE avisado. :)


## Rodando localmente

> Necessário Docker

```bash
sh run.sh
```

API disponível em: [localhost:9999](http://localhost:9999)

Para parar:
```bash
sh stop.sh
```


## Testes de carga

> Necessário **Python 10+**

1. No diretório raíz da aplicação, crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate
```

2. Instale as dependências e rode o teste de carga com o [`Locust`](https://locust.io/):
```bash
pip install -r requirements-dev.txt
locust -f ./api_load_testing/locustfile.py
```

3. Acesse o dashboard em [`localhost:8089`](http://localhost:8089) e defina a quantidade de usuários simultâneos que você quer acessando a API (teste com 100 inicialmente rs)
