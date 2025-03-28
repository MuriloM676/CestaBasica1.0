from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Configuração do Banco de Dados
DATABASE_URL = "sqlite:///./cestas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Usuário no Banco de Dados
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    endereco = Column(String)
    telefone = Column(String, unique=True)
    retirou_cesta = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Inicialização do FastAPI
app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens, você pode especificar domínios específicos se preferir
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, PATCH, etc.)
    allow_headers=["*"],  # Permite todos os header
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota para verificar se a API está funcionando
@app.get("/")
def read_root():
    return {"message": "API está funcionando"}

# Criar um novo usuário
@app.post("/usuarios")
def criar_usuario(nome: str, endereco: str, telefone: str, db: Session = Depends(get_db)):
    usuario = Usuario(nome=nome, endereco=endereco, telefone=telefone)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

# Consultar um usuário pelo ID
@app.get("/usuarios/{id}")
def consultar_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

# Atualizar status de retirada
@app.patch("/usuarios/{id}")
def atualizar_status(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario.retirou_cesta = True
    db.commit()
    return {"message": "Status atualizado com sucesso"}

# Listar todos os usuários
@app.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()