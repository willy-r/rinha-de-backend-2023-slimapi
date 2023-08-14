from uuid import uuid4
from datetime import date
import json

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, constr
import asyncpg
import redis

app = FastAPI()

cache = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)


async def get_database_pool():
    return await asyncpg.create_pool('postgres://postgres:postgres@localhost:5432/postgres')


@app.on_event('startup')
async def app_startup_event():
    async with await get_database_pool() as pool:
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id UUID PRIMARY KEY,
                    apelido VARCHAR(32),
                    nome VARCHAR(100),
                    nascimento DATE,
                    stack VARCHAR[]
                )
                """
            )


@app.on_event('shutdown')
async def app_shutdown_event():
    async with await get_database_pool() as pool:
        async with pool.acquire() as conn:
            await conn.execute('DROP TABLE IF EXISTS pessoas')


def serialize(data):
    return json.dumps(data, default=str)


def deserialize(data):
    return json.loads(data)


class Pessoa(BaseModel):
    apelido: constr(max_length=32)
    nome: constr(max_length=100)
    nascimento: date
    stack: list[constr(max_length=32)] | None


@app.post('/pessoas', status_code=201)
async def create(res: Response, pessoa: Pessoa):
    async with await get_database_pool() as pool:
        async with pool.acquire() as conn:
            record = await conn.fetchrow('SELECT * FROM pessoas WHERE apelido = $1', pessoa.apelido)
            if record:
               raise HTTPException(status_code=422)
            pessoa_id = str(uuid4())
            await conn.execute(
                'INSERT INTO pessoas (id, apelido, nome, nascimento, stack) VALUES ($1, $2, $3, $4, $5)',
                pessoa_id,
                pessoa.apelido,
                pessoa.nome,
                pessoa.nascimento,
                pessoa.stack,
            )
            cache.set(pessoa_id, pessoa.model_dump_json())
            res.headers.update({'Location': f'/pessoas/{pessoa_id}'})


@app.get('/pessoas/{id}')
async def find_by_id(id: str):
    cached_pessoa = cache.get(id)
    if cached_pessoa:
        return {
            "id": id,
            **deserialize(cached_pessoa),
        }
    else:
        async with await get_database_pool() as pool:
            async with pool.acquire() as conn:
                pessoa = await conn.fetchrow('SELECT * FROM pessoas WHERE id = $1', id)
                if pessoa:
                    pessoa_data = dict(pessoa_data)
                    cache.set(pessoa_data['id'], serialize(pessoa_data))
                    return pessoa_data
                else:
                    raise HTTPException(status_code=404)
    

@app.get('/pessoas')
async def find_by_term(t: str = Query(..., min_length=1)):
    async with await get_database_pool() as pool:
        async with pool.acquire() as conn:
            results = await conn.fetch(
                'SELECT * FROM pessoas WHERE apelido ILIKE $1 OR nome ILIKE $2 OR $3 ILIKE ANY(stack)',
                f'%{t}%',
                f'%{t}%',
                t,
            )
            return [dict(row) for row in results]


@app.get("/contagem-pessoas")
async def count_pessoas():
    async with await get_database_pool() as pool:
        async with pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM pessoas")
