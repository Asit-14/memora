from fastapi import FastAPI, Request
from app.database import engine, Base
from app.models import user as user_model
from app.models import note as note_model
from app.models import token_blacklist as blacklist_model
from app.routers import auth, notes
from fastapi.middleware.cors import CORSMiddleware
from  app.core.logger import logger
import time




 
# Create all tables in PostgreSQL automatically
Base.metadata.create_all(bind=engine)
 
app = FastAPI(
    title='crud or  notes api',
    description='crud operation and i added  the  notes  appliaction in this ',
)
 
# Register routers (like app.use('/auth', authRouter) in Express)
app.include_router(auth.router, prefix='/auth', tags=['Authentication'])
app.include_router(notes.router, prefix='/notes', tags=['Notes CRUD'])


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def root():
    return {'message': 'Notes App API running', 'docs': '/docs'}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    user_email = "anonymous"

    # Extract token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            user_email = payload.get("sub")  # or email field
        except:
            pass

    logger.info(f"{request.method} {request.url} | user={user_email}")

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(f"Completed in {duration:.4f}s | user={user_email}")

    return response
    start_time =  time.time()
    user_email = "anonymous"


    auth_header =  request.headers.get("Authorization")
    if  auth_header  and auth_header.startswith("Bearer"):
        token =  auth_header.split(" ")[1]
        try:
            payload =  decode_token(token)
            user_email =  payload.get("sub")
        except:
            pass

    
    logger.info(f"{request.method} {request.url}  | user ={user_email}")
    response =  await call_next(request)

    duration =  time.time()-start_time

    logger.info(f"Completed in {duration : .4f}s  | user = {user_email}" )
    

    return response