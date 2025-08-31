from aiohttp import web
import aiohttp
import asyncio
import json
import os
import signal

class ChatServer:
    def __init__(self):
        self.app = web.Application()
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_get('/health', self.health_check)
        self.clients = {}
        self.messages = []

    async def health_check(self, request):
        return web.json_response({
            'status': 'ok',
            'clients_count': len(self.clients),
            'messages_count': len(self.messages)
        })

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        client_id = None
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        
                        if data.get('type') == 'register':
                            client_id = data.get('userId')
                            if client_id:
                                self.clients[client_id] = ws
                                print(f"✅ Client connected: {client_id}")
                                
                                # Отправляем количество онлайн пользователей
                                await self.broadcast_users_count()
                                
                        elif data.get('type') == 'message' and client_id:
                            message = {
                                'type': 'message',
                                'text': data.get('text', ''),
                                'from': client_id,
                                'timestamp': asyncio.get_event_loop().time()
                            }
                            
                            self.messages.append(message)
                            await self.broadcast_message(message)
                            
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Invalid JSON'
                        }))
                        
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                print(f"❌ Client disconnected: {client_id}")
                await self.broadcast_users_count()
                
        return ws

    async def broadcast_message(self, message):
        for client_id, ws in self.clients.items():
            try:
                await ws.send_str(json.dumps(message))
            except:
                pass

    async def broadcast_users_count(self):
        users_count = len(self.clients)
        for client_id, ws in self.clients.items():
            try:
                await ws.send_str(json.dumps({
                    'type': 'users_online',
                    'count': users_count
                }))
            except:
                pass

async def start_server():
    server = ChatServer()
    runner = web.AppRunner(server.app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("🚀 MAXimalno server started on port 8080")
    print("📡 WebSocket URL: wss://your-codespace-8080.app.github.dev")
    
    # Бесконечное ожидание
    await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(start_server())
