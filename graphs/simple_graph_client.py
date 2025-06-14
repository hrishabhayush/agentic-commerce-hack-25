"""
Simple Graph Client using SQLite - No Docker or Neo4j required!
This provides the same functionality but with SQLite as the backend.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGraphClient:
    """
    Simple graph client using SQLite - much easier than Neo4j!
    """
    
    def __init__(self, db_path: str = "graph.db"):
        """Initialize SQLite connection"""
        try:
            self.db_path = db_path
            self.connection = sqlite3.connect(db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.create_tables()
            logger.info("✅ Successfully connected to SQLite database")
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQLite: {e}")
            raise
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()
        
        # Create nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT,
                content TEXT,
                value REAL,
                timestamp TEXT,
                confidence REAL,
                source TEXT,
                tags TEXT,  -- JSON array as string
                audience_relevance_json TEXT,
                embedding_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create edges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relationship_type TEXT,
                weight REAL,
                confidence REAL,
                semantic_similarity REAL,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES nodes (id),
                FOREIGN KEY (target_id) REFERENCES nodes (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_source ON nodes(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_weight ON edges(weight)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id)")
        
        self.connection.commit()
        logger.info("🔧 Database tables and indexes created")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("SQLite connection closed")
    
    def clear_database(self):
        """Clear all nodes and edges"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM edges")
        cursor.execute("DELETE FROM nodes")
        self.connection.commit()
        logger.info("🗑️ Database cleared")
    
    def load_nodes_from_json(self, nodes_file: str) -> int:
        """Load nodes from JSON file into SQLite"""
        logger.info(f"📥 Loading nodes from {nodes_file}")
        
        with open(nodes_file, 'r') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        loaded_count = 0
        cursor = self.connection.cursor()
        
        for node in nodes:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO nodes 
                    (id, type, content, value, timestamp, confidence, source, tags, 
                     audience_relevance_json, embedding_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    node.get('id'),
                    node.get('type'),
                    node.get('content'),
                    node.get('value'),
                    node.get('timestamp'),
                    node.get('confidence'),
                    node.get('source'),
                    json.dumps(node.get('tags', [])),
                    json.dumps(node.get('audience_relevance', {})),
                    json.dumps(node.get('embedding', []))
                ))
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load node {node.get('id')}: {e}")
        
        self.connection.commit()
        logger.info(f"✅ Loaded {loaded_count} nodes successfully")
        return loaded_count
    
    def load_edges_from_json(self, edges_file: str) -> int:
        """Load edges from JSON file into SQLite"""
        logger.info(f"📥 Loading edges from {edges_file}")
        
        with open(edges_file, 'r') as f:
            data = json.load(f)
        
        edges = data.get('edges', [])
        loaded_count = 0
        cursor = self.connection.cursor()
        
        for edge in edges:
            try:
                cursor.execute("""
                    INSERT INTO edges 
                    (source_id, target_id, relationship_type, weight, confidence, 
                     semantic_similarity, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    edge.get('source_id'),
                    edge.get('target_id'),
                    edge.get('relationship_type'),
                    edge.get('weight'),
                    edge.get('confidence'),
                    edge.get('semantic_similarity'),
                    json.dumps(edge.get('metadata', {}))
                ))
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load edge {edge.get('source_id')} -> {edge.get('target_id')}: {e}")
        
        self.connection.commit()
        logger.info(f"✅ Loaded {loaded_count} edges successfully")
        return loaded_count
    
    def get_graph_overview(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        cursor = self.connection.cursor()
        
        # Total counts
        cursor.execute("SELECT COUNT(*) as total FROM nodes")
        total_nodes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM edges")
        total_relationships = cursor.fetchone()['total']
        
        # Node counts by type
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM nodes 
            GROUP BY type 
            ORDER BY count DESC
        """)
        node_types = [dict(row) for row in cursor.fetchall()]
        
        # Top sources
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM nodes 
            WHERE source IS NOT NULL
            GROUP BY source 
            ORDER BY count DESC 
            LIMIT 10
        """)
        top_sources = [dict(row) for row in cursor.fetchall()]
        
        # High confidence nodes
        cursor.execute("SELECT COUNT(*) as count FROM nodes WHERE confidence >= 0.8")
        high_confidence = cursor.fetchone()['count']
        
        return {
            'total_nodes': total_nodes,
            'total_relationships': total_relationships,
            'node_types': node_types,
            'top_sources': top_sources,
            'high_confidence_nodes': high_confidence,
            'generated_at': datetime.now().isoformat()
        }
    
    def search_nodes(self, query: str, limit: int = 50) -> List[Dict]:
        """Search nodes by content"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, type, content, source, tags, confidence, value, timestamp
            FROM nodes
            WHERE content LIKE ? OR source LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_filtered_graph(self, 
                          node_types: List[str] = None,
                          sources: List[str] = None,
                          min_confidence: float = 0.0,
                          min_weight: float = 0.3,
                          tags: List[str] = None,
                          limit: int = 100) -> Dict:
        """Get filtered graph data"""
        cursor = self.connection.cursor()
        
        # Build dynamic query
        conditions = ["confidence >= ?"]
        params = [min_confidence]
        
        if node_types:
            placeholders = ','.join('?' for _ in node_types)
            conditions.append(f"type IN ({placeholders})")
            params.extend(node_types)
        
        if sources:
            placeholders = ','.join('?' for _ in sources)
            conditions.append(f"source IN ({placeholders})")
            params.extend(sources)
        
        where_clause = " AND ".join(conditions)
        params.append(limit)
        
        # Get filtered nodes
        cursor.execute(f"""
            SELECT id, type, content, source, confidence, value, tags, audience_relevance_json
            FROM nodes
            WHERE {where_clause}
            ORDER BY confidence DESC
            LIMIT ?
        """, params)
        
        nodes = [dict(row) for row in cursor.fetchall()]
        node_ids = [node['id'] for node in nodes]
        
        # Get relationships between filtered nodes
        edges = []
        if node_ids:
            placeholders = ','.join('?' for _ in node_ids)
            cursor.execute(f"""
                SELECT source_id, target_id, weight, confidence, semantic_similarity, 
                       relationship_type, metadata_json
                FROM edges
                WHERE source_id IN ({placeholders}) AND target_id IN ({placeholders})
                  AND weight >= ?
                ORDER BY weight DESC
            """, node_ids + node_ids + [min_weight])
            
            edges = [dict(row) for row in cursor.fetchall()]
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_nodes': len(nodes),
            'total_edges': len(edges)
        }
    
    def get_audience_focused_graph(self, audience: str, limit: int = 100) -> Dict:
        """Get graph focused on specific audience"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, type, content, source, confidence, tags, audience_relevance_json
            FROM nodes
            WHERE audience_relevance_json IS NOT NULL
            ORDER BY confidence DESC
        """)
        
        all_nodes = [dict(row) for row in cursor.fetchall()]
        
        # Filter by audience in Python
        relevant_nodes = []
        for node in all_nodes:
            try:
                audience_data = json.loads(node['audience_relevance_json'])
                if audience_data.get(audience, 0) > 0.0:
                    node['relevance_score'] = audience_data[audience]
                    relevant_nodes.append(node)
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Sort and limit
        relevant_nodes.sort(key=lambda x: x['relevance_score'], reverse=True)
        relevant_nodes = relevant_nodes[:limit]
        
        # Get edges
        edges = []
        if relevant_nodes:
            node_ids = [node['id'] for node in relevant_nodes]
            placeholders = ','.join('?' for _ in node_ids)
            cursor.execute(f"""
                SELECT source_id, target_id, weight, relationship_type
                FROM edges
                WHERE source_id IN ({placeholders}) AND target_id IN ({placeholders})
                  AND weight >= 0.3
                ORDER BY weight DESC
            """, node_ids + node_ids)
            
            edges = [dict(row) for row in cursor.fetchall()]
        
        return {
            'audience': audience,
            'nodes': relevant_nodes,
            'edges': edges,
            'total_nodes': len(relevant_nodes),
            'total_edges': len(edges)
        }

def initialize_simple_graph(nodes_file: str, edges_file: str) -> SimpleGraphClient:
    """Initialize SQLite graph with data"""
    client = SimpleGraphClient()
    
    try:
        # Load data
        client.load_nodes_from_json(nodes_file)
        client.load_edges_from_json(edges_file)
        
        # Get overview
        overview = client.get_graph_overview()
        logger.info(f"🎯 Graph loaded: {overview['total_nodes']} nodes, {overview['total_relationships']} relationships")
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to initialize graph: {e}")
        client.close()
        raise

if __name__ == "__main__":
    # Test the simple graph client
    client = initialize_simple_graph(
        'nodes/flowmetrics_nodes.json',
        'edges/flowmetrics_edges.json'
    )
    
    overview = client.get_graph_overview()
    print(json.dumps(overview, indent=2))
    
    client.close() 