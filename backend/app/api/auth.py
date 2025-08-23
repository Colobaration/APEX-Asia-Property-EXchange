from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.integrations.amo.auth import AmoCRMAuth
from app.core.config import settings
from app.core.db import get_db
from app.core.logging import logger

router = APIRouter()

@router.get("/amo")
async def amo_auth():
    """
    Начало OAuth2 авторизации с amoCRM
    """
    try:
        auth_client = AmoCRMAuth()
        auth_url = auth_client.get_auth_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating auth URL: {str(e)}")

@router.get("/amo/callback")
async def amo_callback(code: str, state: str = None, request: Request = None):
    """
    Callback для получения access token от amoCRM
    """
    try:
        auth_client = AmoCRMAuth()
        tokens = await auth_client.exchange_code_for_tokens(code)
        
        # Сохранение токенов в БД
        success = await auth_client.save_tokens(tokens)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save tokens")
        
        # Редирект на frontend с успешной авторизацией
        return RedirectResponse(
            url=f"{settings.frontend_url}/auth/success?status=success"
        )
        
    except Exception as e:
        logger.error(f"Error in amo callback: {str(e)}")
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
        tokens = await auth_client.get_stored_tokens()
        
        if not tokens:
            raise HTTPException(status_code=401, detail="No stored tokens found")
        
        new_tokens = await auth_client.refresh_tokens(tokens["refresh_token"])
        await auth_client.save_tokens(new_tokens)
        
        return {"status": "success", "message": "Token refreshed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/amo/status")
async def amo_auth_status():
    """
    Проверка статуса авторизации amoCRM
    """
    try:
        auth_client = AmoCRMAuth()
        is_authorized = await auth_client.is_authorized()
        
        if is_authorized:
            tokens = await auth_client.get_stored_tokens()
            return {
                "authorized": True,
                "account_id": tokens.get("account_id"),
                "scope": tokens.get("scope")
            }
        else:
            return {"authorized": False}
            
    except Exception as e:
        logger.error(f"Error checking auth status: {str(e)}")
        return {"authorized": False, "error": str(e)}

@router.post("/amo/revoke")
async def revoke_amo_tokens():
    """
    Отзыв токенов amoCRM
    """
    try:
        auth_client = AmoCRMAuth()
        tokens = await auth_client.get_stored_tokens()
        
        if not tokens:
            raise HTTPException(status_code=401, detail="No stored tokens found")
        
        success = await auth_client.revoke_tokens(tokens["access_token"])
        
        if success:
            return {"status": "success", "message": "Tokens revoked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to revoke tokens")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/amo/test")
async def test_amo_connection():
    """
    Тестирование подключения к amoCRM
    """
    try:
        from app.integrations.amo.client import AmoCRMClient
        client = AmoCRMClient()
        
        # Тест подключения
        connection_ok = await client.test_connection()
        
        if connection_ok:
            # Получаем информацию об аккаунте
            account_info = await client.get_account_info()
            return {
                "status": "success",
                "connection": "ok",
                "account_info": account_info
            }
        else:
            return {
                "status": "error",
                "connection": "failed",
                "message": "Failed to connect to amoCRM"
            }
            
    except Exception as e:
        logger.error(f"Error testing amoCRM connection: {str(e)}")
        return {
            "status": "error",
            "connection": "failed",
            "message": str(e)
        }
