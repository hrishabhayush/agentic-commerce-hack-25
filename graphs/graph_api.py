"""
FastAPI Web Service for Graph Visualization Platform
Provides REST API endpoints similar to Linkurious functionality
"""

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import logging
import asyncio
from datetime import datetime
import os

from neo4j_client import Neo4jGraphClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Agentic Commerce Graph Visualization API",
    description="Professional graph visualization platform inspired by Linkurious",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Neo4j client
neo4j_client: Optional[Neo4jGraphClient] = None

# Pydantic models for API requests
class GraphFilterRequest(BaseModel):
    node_types: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    min_confidence: float = 0.0
    min_weight: float = 0.3
    tags: Optional[List[str]] = None
    limit: int = 100

class SearchRequest(BaseModel):
    query: str
    limit: int = 50

class NeighborRequest(BaseModel):
    node_id: str
    depth: int = 1
    min_weight: float = 0.3

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize Neo4j connection and load data"""
    global neo4j_client
    try:
        logger.info("🚀 Starting Graph Visualization API...")
        
        # Initialize Neo4j client
        neo4j_client = Neo4jGraphClient()
        
        # Check if data exists, if not load it
        overview = neo4j_client.get_graph_overview()
        if overview['total_nodes'] == 0:
            logger.info("📥 Loading initial graph data...")
            neo4j_client.load_nodes_from_json('nodes/flowmetrics_nodes.json')
            neo4j_client.load_edges_from_json('edges/flowmetrics_edges.json')
            overview = neo4j_client.get_graph_overview()
        
        logger.info(f"✅ Graph ready: {overview['total_nodes']} nodes, {overview['total_relationships']} relationships")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize graph API: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close Neo4j connection"""
    global neo4j_client
    if neo4j_client:
        neo4j_client.close()
    logger.info("🔌 Graph API shutdown complete")

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main graph visualization interface"""
    return FileResponse('templates/graph_interface.html')

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "neo4j_connected": neo4j_client is not None
    }

@app.get("/api/overview")
async def get_graph_overview():
    """Get comprehensive graph statistics"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        overview = neo4j_client.get_graph_overview()
        return overview
    except Exception as e:
        logger.error(f"Failed to get overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_nodes(request: SearchRequest):
    """Search nodes with full-text capabilities"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        results = neo4j_client.search_nodes(request.query, request.limit)
        
        # Broadcast search activity to connected clients
        await manager.broadcast({
            "type": "search_activity",
            "query": request.query,
            "results_count": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "query": request.query,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/graph/filtered")
async def get_filtered_graph(request: GraphFilterRequest):
    """Get filtered graph data for visualization"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        graph_data = neo4j_client.get_filtered_graph(
            node_types=request.node_types,
            sources=request.sources,
            min_confidence=request.min_confidence,
            min_weight=request.min_weight,
            tags=request.tags,
            limit=request.limit
        )
        
        # Broadcast filter activity
        await manager.broadcast({
            "type": "filter_activity",
            "filters": request.dict(),
            "results_count": graph_data['total_nodes'],
            "timestamp": datetime.now().isoformat()
        })
        
        return graph_data
    except Exception as e:
        logger.error(f"Filtered graph failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/audience/{audience}")
async def get_audience_graph(audience: str, limit: int = Query(100, ge=1, le=500)):
    """Get audience-focused graph (investors, customers, etc.)"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        graph_data = neo4j_client.get_audience_focused_graph(audience, limit)
        return graph_data
    except Exception as e:
        logger.error(f"Audience graph failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/node/neighbors")
async def get_node_neighbors(request: NeighborRequest):
    """Get node neighbors with relationship details"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        neighbors = neo4j_client.get_node_neighbors(
            request.node_id, 
            request.depth, 
            request.min_weight
        )
        return neighbors
    except Exception as e:
        logger.error(f"Get neighbors failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics_summary():
    """Get advanced analytics and insights"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        analytics = neo4j_client.get_analytics_summary()
        return analytics
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources")
async def get_available_sources():
    """Get list of available data sources"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        overview = neo4j_client.get_graph_overview()
        sources = [item['source'] for item in overview['top_sources']]
        return {"sources": sources}
    except Exception as e:
        logger.error(f"Get sources failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/node-types")
async def get_node_types():
    """Get available node types"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        overview = neo4j_client.get_graph_overview()
        types = [item['type'] for item in overview['node_types']]
        return {"node_types": types}
    except Exception as e:
        logger.error(f"Get node types failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/graph")
async def export_graph_data(
    format: str = Query("json", regex="^(json|csv|graphml)$"),
    node_types: Optional[str] = Query(None),
    sources: Optional[str] = Query(None)
):
    """Export graph data in various formats"""
    if not neo4j_client:
        raise HTTPException(status_code=500, detail="Neo4j client not initialized")
    
    try:
        # Parse filters
        node_type_list = node_types.split(',') if node_types else None
        source_list = sources.split(',') if sources else None
        
        # Get filtered data
        graph_data = neo4j_client.get_filtered_graph(
            node_types=node_type_list,
            sources=source_list,
            limit=1000  # Higher limit for export
        )
        
        if format == "json":
            return graph_data
        elif format == "csv":
            # Convert to CSV format
            import pandas as pd
            nodes_df = pd.DataFrame(graph_data['nodes'])
            edges_df = pd.DataFrame(graph_data['edges'])
            
            return {
                "nodes_csv": nodes_df.to_csv(index=False),
                "edges_csv": edges_df.to_csv(index=False)
            }
        elif format == "graphml":
            # Basic GraphML export
            return {"message": "GraphML export coming soon"}
            
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time collaboration
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time graph updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            
            elif data.get("type") == "node_selection":
                # Broadcast node selection to other clients
                await manager.broadcast({
                    "type": "node_selected",
                    "node_id": data.get("node_id"),
                    "user": data.get("user", "anonymous"),
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "graph_update":
                # Handle graph updates
                await manager.broadcast({
                    "type": "graph_changed",
                    "change": data.get("change"),
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Serve static files for the web interface
app.mount("/static", StaticFiles(directory="static"), name="static")

# Development server function
def start_server():
    """Start the development server"""
    import uvicorn
    
    logger.info("🌐 Starting Graph Visualization Server...")
    logger.info("📊 Dashboard will be available at: http://localhost:8000")
    logger.info("🔍 API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        "graph_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server() 