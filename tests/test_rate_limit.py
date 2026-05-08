import pytest
from fastapi import Request, HTTPException
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.dependencies import rate_limit

@pytest.fixture
def mock_redis_pipeline():
    mock_pipe = MagicMock()
    mock_pipe.execute = AsyncMock()
    
    mock_pipeline_obj = MagicMock()
    mock_pipeline_obj.__aenter__.return_value = mock_pipe
    mock_pipeline_obj.__aexit__.return_value = None
    
    mock_client = MagicMock()
    mock_client.pipeline.return_value = mock_pipeline_obj
    mock_client.zrem = AsyncMock()
    
    return mock_client, mock_pipe

@pytest.mark.asyncio
async def test_rate_limit_anonymous_under_limit(mock_redis_pipeline):
    mock_client, mock_pipe = mock_redis_pipeline
    mock_pipe.execute.return_value = [None, None, 1, None] 
    
    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "headers": []})
    
    await rate_limit(request=request, token=None, redis=mock_client)

@pytest.mark.asyncio
async def test_rate_limit_anonymous_over_limit(mock_redis_pipeline):
    mock_client, mock_pipe = mock_redis_pipeline
    mock_pipe.execute.return_value = [None, None, 3, None] 
    
    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "headers": []})
    
    with pytest.raises(HTTPException) as exc_info:
        await rate_limit(request=request, token=None, redis=mock_client)
    assert exc_info.value.status_code == 429
    assert exc_info.value.detail == "Too Many Requests"

@pytest.mark.asyncio
@patch("app.core.dependencies.verify_token_type")
async def test_rate_limit_authenticated_under_limit(mock_verify, mock_redis_pipeline):
    mock_verify.return_value = "test-user-id"
    
    mock_client, mock_pipe = mock_redis_pipeline
    mock_pipe.execute.return_value = [None, None, 5, None] 
    
    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "headers": []})
    
    await rate_limit(request=request, token="valid_token", redis=mock_client)

@pytest.mark.asyncio
@patch("app.core.dependencies.verify_token_type")
async def test_rate_limit_authenticated_over_limit(mock_verify, mock_redis_pipeline):
    mock_verify.return_value = "test-user-id"
    
    mock_client, mock_pipe = mock_redis_pipeline
    mock_pipe.execute.return_value = [None, None, 11, None] 
    
    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "headers": []})
    
    with pytest.raises(HTTPException) as exc_info:
        await rate_limit(request=request, token="valid_token", redis=mock_client)
    assert exc_info.value.status_code == 429
    assert exc_info.value.detail == "Too Many Requests"