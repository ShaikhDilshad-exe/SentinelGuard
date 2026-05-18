import sys
import os
import uuid
import asyncio
import logging

from time import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------
# ENSURE PYTHON CAN FIND PROJECT MODULES
# ---------------------------------------------------------
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

print(f"DEBUG: Python is looking in: {sys.path[-1]}")

# ---------------------------------------------------------
# IMPORT CORE DEPENDENCIES
# ---------------------------------------------------------
from backend.dependencies import (
    alert_manager,
    event_collector,
    analyzer,
    file_monitor,
    network_monitor,
    process_monitor
)

from backend.utils.config import config

from backend.utils.websocket_manager import (
    manager as ws_manager
)

# ---------------------------------------------------------
# IMPORT ROUTES
# ---------------------------------------------------------
from backend.routes import (
    auth_routes,
    monitoring_routes,
    alerts_routes,
    scan_routes
)

# ---------------------------------------------------------
# LOGGER
# ---------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# WEBSOCKET CALLBACK
# ---------------------------------------------------------
main_loop = None


def websocket_alert_callback(alert: dict):

    global main_loop

    try:

        if main_loop and main_loop.is_running():

            main_loop.call_soon_threadsafe(
                lambda: asyncio.create_task(
                    ws_manager.broadcast(alert)
                )
            )

    except Exception as e:

        logger.error(
            f"WebSocket Callback Error: {e}"
        )


# Subscribe callback
alert_manager.subscribe(websocket_alert_callback)

# ---------------------------------------------------------
# DEBUG WATCH PATHS
# ---------------------------------------------------------
print(
    f"[*] DEBUG: SentinelGuard is currently watching: "
    f"{config.WATCH_PATHS}"
)

# ---------------------------------------------------------
# CENTRAL THREAT DETECTION LOOP
# ---------------------------------------------------------
async def threat_detection_loop():

    print(
        ">>> SUCCESS: Central Threat Detection Engine activated."
    )

    while True:

        try:

            events = event_collector.flush_events()

            if events:

                # -------------------------------------------------
                # BROADCAST RAW EVENTS
                # -------------------------------------------------
                for event in events:

                    await ws_manager.broadcast({
                        "type": "event",
                        "payload": event
                    })

                # -------------------------------------------------
                # ANALYZE EVENTS
                # -------------------------------------------------
                try:

                    analysis = analyzer.analyze_behavior(events)

                    threat_level = analysis.get(
                        "threat_level",
                        "none"
                    ).lower()

                    print(
                        f"\n[🧠 BRAIN DECISION] "
                        f"Score: {analysis.get('confidence_score')} "
                        f"| Level: {threat_level}"
                    )

                    if analysis.get("matched_rules"):

                        rules_list = [
                            r["rule"]
                            for r in analysis["matched_rules"]
                        ]

                        print(
                            f"   -> Rules Tripped: {rules_list}"
                        )

                        # -------------------------------------------------
                        # GENERATE ALERT
                        # -------------------------------------------------
                        if threat_level in [
                            "low",
                            "medium",
                            "high",
                            "critical"
                        ]:

                            alert_payload = {

                                "id": str(uuid.uuid4()),

                                "severity": (
                                    threat_level.upper()
                                ),

                                "message": analysis.get(
                                    "explanation",
                                    "Suspicious activity detected"
                                ),

                                "source": "Heuristic Engine",

                                "timestamp": time()
                            }

                            # Broadcast alert
                            await ws_manager.broadcast({

                                "type": "alert",

                                "payload": alert_payload
                            })

                            print(
                                f"📡 SENT TO FRONTEND: "
                                f"{alert_payload['message']}"
                            )

                except Exception as e:

                    print(
                        f"\n[💥 BRAIN CRASHED] "
                        f"Error during analysis: {e}"
                    )

        except Exception as main_e:

            print(
                f"[!] Engine loop error: {main_e}"
            )

        # Wait before next detection cycle
        await asyncio.sleep(5)

# ---------------------------------------------------------
# FASTAPI LIFESPAN
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):

    # -----------------------------------------------------
    # WATCH TEST DIRECTORY
    # -----------------------------------------------------
    test_path = (
        r"D:\capstone\SentinelGuard\Sentinel_Test"
    )

    file_monitor.watch_paths = [
        Path(test_path)
    ]

    print(
        f"[*] CAMERA RESET. STRICTLY WATCHING: "
        f"{file_monitor.watch_paths}"
    )

    # -----------------------------------------------------
    # STORE EVENT LOOP
    # -----------------------------------------------------
    global main_loop

    main_loop = asyncio.get_running_loop()

    # -----------------------------------------------------
    # START MONITORS
    # -----------------------------------------------------
    file_monitor.start()
    network_monitor.start()
    process_monitor.start()

    # -----------------------------------------------------
    # START DETECTION LOOP
    # -----------------------------------------------------
    detection_task = asyncio.create_task(
        threat_detection_loop()
    )

    yield

    # -----------------------------------------------------
    # CLEANUP
    # -----------------------------------------------------
    detection_task.cancel()

    file_monitor.stop()
    network_monitor.stop()
    process_monitor.stop()

# ---------------------------------------------------------
# FASTAPI APP INITIALIZATION
# ---------------------------------------------------------
app = FastAPI(
    lifespan=lifespan,
    title="SentinelGuard API"
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://localhost",
        "http://127.0.0.1:3000"
    ],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ---------------------------------------------------------
# REGISTER ROUTES
# ---------------------------------------------------------
app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    monitoring_routes.router,
    prefix="/api/monitoring",
    tags=["Monitoring"]
)

app.include_router(
    alerts_routes.router,
    prefix="/api/alerts",
    tags=["Alerts"]
)

app.include_router(
    scan_routes.router,
    prefix="/api/scan",
    tags=["Scanning"]
)

# ---------------------------------------------------------
# WEBSOCKET ENDPOINT
# ---------------------------------------------------------
@app.websocket("/ws/alerts")
async def websocket_endpoint(
    websocket: WebSocket
):

    await ws_manager.connect(websocket)

    print("✅ WebSocket Client Connected")

    try:

        while True:

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        ws_manager.disconnect(websocket)

        print("❌ WebSocket Client Disconnected")