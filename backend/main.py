"""
SmartV2V: Software-Based Vehicle-to-Vehicle Communication and Collision Warning System
Main FastAPI Application & WebSocket Server
"""
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.simulation_engine import SimulationEngine
from app.api.routes import router as api_router
import app.api.routes as routes_module
from app.api.websocket_manager import ws_manager

# Authoritative simulation engine instance
simulation_engine = SimulationEngine(settings)
routes_module.sim_engine = simulation_engine

# Streaming task to broadcast to WebSocket clients at 20 Hz
async def websocket_broadcast_worker():
    while True:
        try:
            if ws_manager.active_connections:
                snapshot = simulation_engine.get_full_state_snapshot()
                await ws_manager.broadcast_state(snapshot)
            await asyncio.sleep(0.05)  # 20 Hz WebSocket update stream
        except asyncio.CancelledError:
            break
        except Exception as e:
            await asyncio.sleep(0.1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background WebSocket broadcaster
    broadcast_task = asyncio.create_task(websocket_broadcast_worker())
    # Start the simulation automatically in running state for immediate interactivity
    await simulation_engine.start()
    yield
    # Cleanup on shutdown
    await simulation_engine.stop()
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="SmartV2V — Automotive V2V & Collision Warning Platform",
    description="Software Defined Vehicle (SDV) Real-time V2V Simulator and Safety Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach REST routes
app.include_router(api_router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    # Send immediate initial state
    await websocket.send_text(json.dumps(simulation_engine.get_full_state_snapshot()))
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                cmd_type = cmd.get("type")
                if cmd_type == "start":
                    await simulation_engine.start()
                elif cmd_type == "pause":
                    await simulation_engine.pause()
                elif cmd_type == "resume":
                    await simulation_engine.resume()
                elif cmd_type == "stop":
                    await simulation_engine.stop()
                elif cmd_type == "reset":
                    simulation_engine.reset()
                elif cmd_type == "scenario":
                    scenario_id = cmd.get("scenario_id")
                    if scenario_id:
                        simulation_engine.load_scenario(scenario_id)
                elif cmd_type == "emergency_brake":
                    v_id = cmd.get("vehicle_id")
                    if v_id:
                        simulation_engine.trigger_emergency_brake(v_id)
                elif cmd_type == "settings":
                    settings_dict = cmd.get("settings", {})
                    for k, v in settings_dict.items():
                        if hasattr(simulation_engine.settings, k):
                            setattr(simulation_engine.settings, k, v)
                
                # Acknowledge immediately with updated snapshot
                await websocket.send_text(json.dumps(simulation_engine.get_full_state_snapshot()))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Check for production frontend build in multiple standard locations
FRONTEND_DIST_PATHS = [
    Path(__file__).parent.parent / "frontend" / "dist",
    Path(__file__).parent / "static",
    Path("/app/frontend/dist"),
]

frontend_dist = next((p for p in FRONTEND_DIST_PATHS if p.exists() and (p / "index.html").exists()), None)

if frontend_dist:
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Allow API routes and WS to be handled first
        if full_path.startswith("api") or full_path.startswith("ws") or full_path == "docs" or full_path == "openapi.json":
            return None
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
