from fastapi import APIRouter
from app.api.v1.endpoints import auth, documents, query, users, storage, payments, feedback

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])