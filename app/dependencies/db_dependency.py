from fastapi import Depends
from app.db import get_async_session

db_dependency = Depends(get_async_session)
