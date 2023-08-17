from uuid import uuid4
from datetime import date
import json

from fastapi import FastAPI, HTTPException, Query, Response, Depends
from pydantic import BaseModel, constr
from sqlalchemy import create_engine, Column, Uuid, String, Date, ARRAY, or_, cast
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import redis

import settings

app = FastAPI(title='Rinha de Back-end 2023')

engine = create_engine(settings.DATABASE_URL, pool_size=settings.DATABASE_MAX_CONNECTIONS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PessoaModel(Base):
    __tablename__ = 'pessoas'

    id = Column(Uuid, primary_key=True)
    apelido = Column(String(32), unique=True)
    nome = Column(String(100))
    nascimento = Column(Date)
    stack = Column(ARRAY(String(32)), nullable=True)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        # This will handle closing the session whatever it happens on request
        # when using Depends of FastAPI on a route function.
        session.close()


cache = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)


@app.on_event('startup')
def app_startup_event():
    Base.metadata.create_all(bind=engine)


@app.on_event('shutdown')
def app_shutdown_event():
    Base.metadata.drop_all(bind=engine)


def serialize(data):
    return json.dumps(data, default=str)


def deserialize(data):
    return json.loads(data)


class PessoaSchema(BaseModel):
    apelido: constr(max_length=32)
    nome: constr(max_length=100)
    nascimento: date
    stack: list[constr(max_length=32)] | None


@app.post('/pessoas', status_code=201)
def create(res: Response, pessoa: PessoaSchema, session: Session = Depends(get_session)):
    pessoa_db = session.query(PessoaModel).filter_by(apelido=pessoa.apelido).first()
    if pessoa_db:
        raise HTTPException(status_code=422)
    pessoa_id = str(uuid4())
    new_pessoa = PessoaModel(**{**pessoa.model_dump(), 'id': pessoa_id})
    session.add(new_pessoa)
    session.commit()
    cache.set(pessoa_id, pessoa.model_dump_json())
    res.headers.update({'Location': f'/pessoas/{pessoa_id}'})


@app.get('/pessoas/{id}')
async def find_by_id(id: str, session: Session = Depends(get_session)):
    cached_pessoa = cache.get(id)
    if cached_pessoa:
        return {
            "id": id,
            **deserialize(cached_pessoa),
        }
    pessoa = session.query(PessoaModel).filter_by(id=id).first()
    if pessoa:
        pessoa_data = dict(pessoa)
        cache.set(pessoa_data['id'], serialize(pessoa_data))
        return pessoa_data
    else:
        raise HTTPException(status_code=404)


@app.get('/pessoas')
def find_by_term(t: str = Query(..., min_length=1), session: Session = Depends(get_session)):
    return session.query(PessoaModel).filter(
        or_(PessoaModel.apelido.ilike(f'%{t}%'),
            PessoaModel.nome.ilike(f'%{t}%'),
            cast(PessoaModel.stack, String).ilike(f'%{t}%'))
    ).limit(50).all()


@app.get("/contagem-pessoas")
def count_pessoas(session: Session = Depends(get_session)):
    return session.query(PessoaModel).count()
