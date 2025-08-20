from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.integrations.amo.auth import AmoCRMAuth
from app.core.config import settings

router = APIRouter()

@router.get("/amo")
async def amo_auth():
    """
    Начало OAuth2 авторизации с amoCRM
    """
    auth_client = AmoCRMAuth()
    auth_url = auth_client.get_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/amo/callback")
async def amo_callback(code: str, request: Request):
    """
    Callback для получения access token от amoCRM
    """
    try:
        auth_client = AmoCRMAuth()
        tokens = await auth_client.exchange_code_for_tokens(code)
        
        # Сохранение токенов в БД или кэше
        await auth_client.save_tokens(tokens)
        
        # Редирект на frontend с успешной авторизацией
        return RedirectResponse(
            url=f"{settings.frontend_url}/auth/success?status=success"
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"{settings.frontend_url}/auth/error?error={str(e)}"
        )

@router.post("/amo/refresh")
async def refresh_amo_token():
    """
    Обновление access token amoCRM
    """
    try:
        auth_client = AmoCRMAuth()
        new_tokens = await auth_client.refresh_access_token()
        return {"status": "success", "message": "Token refreshed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/amo/status")
async def amo_auth_status():
    """
    Проверка статуса авторизации amoCRM
    """
    auth_client = AmoCRMAuth()
    is_authorized = await auth_client.is_authorized()
    return {"authorized": is_authorized}
