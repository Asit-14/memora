from fastapi import FastAPI
from app.database import engine, Base
from app.models import user as user_model
from app.models import note as note_model
from app.models import token_blacklist as blacklist_model
from app.routers import auth, notes
 
# Create all tables in PostgreSQL automatically
Base.metadata.create_all(bind=engine)
 
app = FastAPI(
    title='Notes App API',
    description='CRUD Notes with JWT Auth and PostgreSQL',
    version='1.0.0'
)
 
# Register routers (like app.use('/auth', authRouter) in Express)
app.include_router(auth.router, prefix='/auth', tags=['Authentication'])
app.include_router(notes.router, prefix='/notes', tags=['Notes CRUD'])

@app.get('/')
def root():
    return {'message': 'Notes App API running', 'docs': '/docs'}
