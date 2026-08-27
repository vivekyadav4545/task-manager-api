import json
import redis.asyncio as redis
from config import settings


redis_client = redis.from_url(settings.redis_url , decode_responses=True)
TASK_CACHE_TTL = 300  # seconds

def task_key(user_id:int , task_id:int)->str:
    return f"user:{user_id}:task:{task_id}"

def task_list_key(user_id:int , skip:int , limit:int)->str:
    return f"user:{user_id}:skip:{skip}:limit:{limit}"

async def get_cached(key:str):
    val = await redis_client.get(key)
    return json.loads(val) if val else None

async def set_cached(key:str ,value , ttl: int = TASK_CACHE_TTL):
    await redis_client.set(key , json.dumps(value) ,ex=ttl)

async def invalidate_user_tasks(user_id:int):
    pattern = f"user:{user_id}:task*"

    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)