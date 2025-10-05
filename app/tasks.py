import redis.asyncio as redis
import asyncio
import json
from app.config import settings
from app.ws_manager import ws_manager

REDIS_CHANNEL = "delays_channel"

async def publish_delay(redis, payload: dict):
    await redis.publish(REDIS_CHANNEL, json.dumps(payload))

async def redis_listener():
    redis_client = redis.from_url("redis://redis", decode_responses=True)
    sub = redis_client.pubsub()
    await sub.subscribe(REDIS_CHANNEL)
    async for message in sub.listen():
        if message is None:
            continue
        if message['type'] != 'message':
            continue
        data = json.loads(message['data'])
        # Broadcast to websockets
        await ws_manager.broadcast(data, topic="global")
        # Here you can also trigger push notifications via FCM/APNs (placeholder)
        # await send_push_notifications(data)

# In main.py we'll start redis_listener as background task
