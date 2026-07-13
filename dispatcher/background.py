import asyncio
import structlog
import time
import json
from shared.models import NodeHealth
from dispatcher.queue.redis_queue import queue

logger = structlog.get_logger()

async def check_node_heartbeats():
    """
    Background task to evict nodes that haven't sent a heartbeat recently.
    Marks them as UNHEALTHY after 3 missed beats (15s).
    """
    logger.info("Starting background node heartbeat monitor")
    while True:
        try:
            nodes_raw = await queue.redis.hgetall(queue.nodes_key)
            now = time.time()
            for node_id, raw_data in nodes_raw.items():
                node = json.loads(raw_data)
                last_hb = node.get("last_heartbeat", now)
                
                if now - last_hb > 15 and node.get("health") != NodeHealth.UNHEALTHY.value:
                    logger.warning("Node missed 3 heartbeats. Marking UNHEALTHY.", node_id=node_id)
                    node["health"] = NodeHealth.UNHEALTHY.value
                    await queue.redis.hset(queue.nodes_key, node_id, json.dumps(node))
                    
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            logger.info("Stopping background node heartbeat monitor")
            break
        except Exception as e:
            logger.error("Error in heartbeat monitor", error=str(e))
            await asyncio.sleep(10)
