from uuid import uuid4
from datetime import date
import json

from fastapi import FastAPI, HTTPException, Query, Response, Request, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from sqlalchemy import create_engine, Column, Uuid, String, Date, ARRAY, or_, cast
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import redis

import settings

# FastAPI
app = FastAPI(title='Rinha de Back-end 2023')

# Redis
cache = redis.StrictRedis(host=settings.CACHE_HOST, port=settings.CACHE_PORT, decode_responses=True)

# SQLAlchemy
engine = create_engine(settings.DATABASE_URL, pool_size=settings.DATABASE_MAX_CONNECTIONS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PessoaModel(Base):
    __tablename__ = 'pessoas'

    id = Column(Uuid, primary_key=True, default=uuid4)
    apelido = Column(String(32))
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


Base.metadata.create_all(bind=engine)


@app.on_event('shutdown')
def app_shutdown_event():
    Base.metadata.drop_all(bind=engine)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, exc: RequestValidationError):
    details = exc.errors()
    if any(detail['type'] == 'string_type' and isinstance(detail['input'], int) for detail in details):
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder({'detail': details}),
        )    
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({'detail': details}),
    )


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
    cached_pessoa = cache.get(pessoa.apelido)
    if cached_pessoa:
        raise HTTPException(status_code=422)
    new_pessoa = PessoaModel(**pessoa.model_dump())
    session.add(new_pessoa)
    session.commit()
    cache.set(new_pessoa.apelido, new_pessoa.apelido)
    cache.set(str(new_pessoa.id), serialize(new_pessoa.__dict__))
    res.headers.update({'Location': f'/pessoas/{new_pessoa.id}'})


@app.get('/pessoas/{id}')
async def find_by_id(id: str, session: Session = Depends(get_session)):
    cached_pessoa = cache.get(id)
    if cached_pessoa:
        return deserialize(cached_pessoa)
    pessoa = session.query(PessoaModel).get(id)
    if pessoa:
        pessoa_data = pessoa.__dict__
        cache.set(pessoa.apelido, pessoa.apelido)
        cache.set(str(pessoa.id), serialize(pessoa_data))
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
