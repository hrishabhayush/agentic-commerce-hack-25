"""
Neo4j Graph Database Client for Agentic Commerce Graph Visualization
Provides powerful graph database operations similar to Linkurious platform
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jGraphClient:
    """
    Professional Neo4j client for graph visualization platform
    Inspired by Linkurious capabilities
    """
    
    def __init__(self, uri: str = "neo4j://127.0.0.1:7687", 
                 username: str = "neo4j", 
                 password: str = "password"):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.verify_connectivity()
            logger.info("✅ Successfully connected to Neo4j database")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def verify_connectivity(self):
        """Verify database connection"""
        with self.driver.session() as session:
            result = session.run("CALL db.ping()")
            result.consume()
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def clear_database(self):
        """Clear all nodes and relationships - use with caution!"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("🗑️ Database cleared")
    
    def create_constraints(self):
        """Create database constraints for optimal performance"""
        constraints = [
            "CREATE CONSTRAINT unique_node_id IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT unique_metric_id IF NOT EXISTS FOR (m:Metric) REQUIRE m.id IS UNIQUE", 
            "CREATE CONSTRAINT unique_insight_id IF NOT EXISTS FOR (i:Insight) REQUIRE i.id IS UNIQUE",
            "CREATE INDEX node_type_index IF NOT EXISTS FOR (n:Node) ON (n.type)",
            "CREATE INDEX node_source_index IF NOT EXISTS FOR (n:Node) ON (n.source)",
            "CREATE INDEX node_tags_index IF NOT EXISTS FOR (n:Node) ON (n.tags)",
            "CREATE INDEX relationship_weight_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.weight)"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.warning(f"Constraint/Index already exists or failed: {e}")
        
        logger.info("🔧 Database constraints and indexes created")
    
    def load_nodes_from_json(self, nodes_file: str) -> int:
        """Load nodes from JSON file into Neo4j"""
        logger.info(f"📥 Loading nodes from {nodes_file}")
        
        with open(nodes_file, 'r') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        loaded_count = 0
        
        with self.driver.session() as session:
            for node in nodes:
                # Create node with appropriate label based on type
                node_type = node.get('type', 'Node').capitalize()
                
                query = f"""
                CREATE (n:{node_type}:Node {{
                    id: $id,
                    type: $type,
                    content: $content,
                    value: $value,
                    timestamp: $timestamp,
                    confidence: $confidence,
                    source: $source,
                    tags: $tags,
                    audience_relevance_json: $audience_relevance_json,
                    embedding_json: $embedding_json,
                    created_at: datetime()
                }})
                """
                
                try:
                    session.run(query, {
                        'id': node.get('id'),
                        'type': node.get('type'),
                        'content': node.get('content'),
                        'value': node.get('value'),
                        'timestamp': node.get('timestamp'),
                        'confidence': node.get('confidence'),
                        'source': node.get('source'),
                        'tags': node.get('tags', []),
                        'audience_relevance_json': json.dumps(node.get('audience_relevance', {})),
                        'embedding_json': json.dumps(node.get('embedding', []))
                    })
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"Failed to load node {node.get('id')}: {e}")
        
        logger.info(f"✅ Loaded {loaded_count} nodes successfully")
        return loaded_count
    
    def load_edges_from_json(self, edges_file: str) -> int:
        """Load edges from JSON file into Neo4j"""
        logger.info(f"📥 Loading edges from {edges_file}")
        
        with open(edges_file, 'r') as f:
            data = json.load(f)
        
        edges = data.get('edges', [])
        loaded_count = 0
        
        with self.driver.session() as session:
            for edge in edges:
                query = """
                MATCH (source {id: $source_id})
                MATCH (target {id: $target_id})
                CREATE (source)-[r:RELATES_TO {
                    relationship_type: $relationship_type,
                    weight: $weight,
                    confidence: $confidence,
                    semantic_similarity: $semantic_similarity,
                    metadata_json: $metadata_json,
                    created_at: datetime()
                }]->(target)
                """
                
                try:
                    session.run(query, {
                        'source_id': edge.get('source_id'),
                        'target_id': edge.get('target_id'),
                        'relationship_type': edge.get('relationship_type'),
                        'weight': edge.get('weight'),
                        'confidence': edge.get('confidence'),
                        'semantic_similarity': edge.get('semantic_similarity'),
                        'metadata_json': json.dumps(edge.get('metadata', {}))
                    })
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"Failed to load edge {edge.get('source_id')} -> {edge.get('target_id')}: {e}")
        
        logger.info(f"✅ Loaded {loaded_count} edges successfully")
        return loaded_count
    
    def get_graph_overview(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        with self.driver.session() as session:
            # Node counts by type
            node_counts = session.run("""
                MATCH (n:Node)
                RETURN n.type as type, count(n) as count
                ORDER BY count DESC
            """).data()
            
            # Relationship counts
            rel_counts = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """).data()
            
            # Top sources
            top_sources = session.run("""
                MATCH (n:Node)
                WHERE n.source IS NOT NULL
                RETURN n.source as source, count(n) as count
                ORDER BY count DESC
                LIMIT 10
            """).data()
            
            # High confidence nodes
            high_confidence = session.run("""
                MATCH (n:Node)
                WHERE n.confidence >= 0.8
                RETURN count(n) as high_confidence_count
            """).single()
            
            # Total stats
            total_nodes = session.run("MATCH (n) RETURN count(n) as total").single()['total']
            total_relationships = session.run("MATCH ()-[r]->() RETURN count(r) as total").single()['total']
            
            return {
                'total_nodes': total_nodes,
                'total_relationships': total_relationships,
                'node_types': node_counts,
                'relationship_types': rel_counts,
                'top_sources': top_sources,
                'high_confidence_nodes': high_confidence['high_confidence_count'] if high_confidence else 0,
                'generated_at': datetime.now().isoformat()
            }
    
    def search_nodes(self, query: str, limit: int = 50) -> List[Dict]:
        """Advanced node search with full-text capabilities"""
        with self.driver.session() as session:
            # Search in content, source, and tags
            search_query = """
            MATCH (n:Node)
            WHERE toLower(n.content) CONTAINS toLower($query)
               OR toLower(n.source) CONTAINS toLower($query)
               OR any(tag IN n.tags WHERE toLower(tag) CONTAINS toLower($query))
            RETURN n.id as id, n.type as type, n.content as content, 
                   n.source as source, n.tags as tags, n.confidence as confidence,
                   n.value as value, n.timestamp as timestamp
            ORDER BY n.confidence DESC
            LIMIT $limit
            """
            
            results = session.run(search_query, {'query': query, 'limit': limit})
            return [dict(record) for record in results]
    
    def get_node_neighbors(self, node_id: str, depth: int = 1, min_weight: float = 0.3) -> Dict:
        """Get node and its neighbors with relationship details"""
        with self.driver.session() as session:
            query = f"""
            MATCH path = (center:Node {{id: $node_id}})-[r:RELATES_TO*1..{depth}]-(neighbor:Node)
            WHERE all(rel in relationships(path) WHERE rel.weight >= $min_weight)
            WITH center, neighbor, relationships(path) as rels
            RETURN center.id as center_id, center.content as center_content, center.type as center_type,
                   collect(DISTINCT {{
                       id: neighbor.id,
                       content: neighbor.content,
                       type: neighbor.type,
                       source: neighbor.source,
                       confidence: neighbor.confidence,
                       relationship_weight: [rel in rels | rel.weight][0]
                   }}) as neighbors
            """
            
            result = session.run(query, {
                'node_id': node_id, 
                'min_weight': min_weight
            }).single()
            
            if result:
                return dict(result)
            return {}
    
    def get_filtered_graph(self, 
                          node_types: List[str] = None,
                          sources: List[str] = None,
                          min_confidence: float = 0.0,
                          min_weight: float = 0.3,
                          tags: List[str] = None,
                          limit: int = 100) -> Dict:
        """Get filtered graph data for visualization"""
        conditions = ["n.confidence >= $min_confidence"]
        params = {'min_confidence': min_confidence, 'min_weight': min_weight, 'limit': limit}
        
        if node_types:
            conditions.append("n.type IN $node_types")
            params['node_types'] = node_types
        
        if sources:
            conditions.append("n.source IN $sources")
            params['sources'] = sources
        
        if tags:
            conditions.append("any(tag IN n.tags WHERE tag IN $tags)")
            params['tags'] = tags
        
        where_clause = " AND ".join(conditions)
        
        with self.driver.session() as session:
            # Get filtered nodes
            nodes_query = f"""
            MATCH (n:Node)
            WHERE {where_clause}
            RETURN n.id as id, n.type as type, n.content as content,
                   n.source as source, n.confidence as confidence, n.value as value,
                   n.tags as tags, n.audience_relevance_json as audience_relevance_json
            ORDER BY n.confidence DESC
            LIMIT $limit
            """
            
            nodes = session.run(nodes_query, params).data()
            node_ids = [node['id'] for node in nodes]
            
            # Get relationships between filtered nodes
            if node_ids:
                edges_query = """
                MATCH (source:Node)-[r:RELATES_TO]->(target:Node)
                WHERE source.id IN $node_ids AND target.id IN $node_ids
                  AND r.weight >= $min_weight
                RETURN source.id as source_id, target.id as target_id,
                       r.weight as weight, r.confidence as confidence,
                       r.semantic_similarity as semantic_similarity,
                       r.relationship_type as relationship_type,
                       r.metadata_json as metadata_json
                ORDER BY r.weight DESC
                """
                
                edges = session.run(edges_query, {
                    'node_ids': node_ids,
                    'min_weight': min_weight
                }).data()
            else:
                edges = []
            
            return {
                'nodes': nodes,
                'edges': edges,
                'filters_applied': {
                    'node_types': node_types,
                    'sources': sources,
                    'min_confidence': min_confidence,
                    'min_weight': min_weight,
                    'tags': tags
                },
                'total_nodes': len(nodes),
                'total_edges': len(edges)
            }
    
    def get_audience_focused_graph(self, audience: str, limit: int = 25) -> Dict:
        """Get a focused graph for specific audience with relevant insights and connections"""
        with self.driver.session() as session:
            try:
                # Get all nodes with their audience relevance data
                query = """
                MATCH (n:Node)
                WHERE n.audience_relevance_json IS NOT NULL
                RETURN n.id as id, n.type as type, n.content as content,
                       n.source as source, n.confidence as confidence, n.tags as tags,
                       n.audience_relevance_json as audience_relevance_json, n.value as value
                ORDER BY n.confidence DESC
                """
                
                all_nodes = session.run(query).data()
                
                # Filter and score nodes by audience relevance
                audience_nodes = []
                for node in all_nodes:
                    try:
                        audience_data = json.loads(node['audience_relevance_json'])
                        relevance_score = audience_data.get(audience, 0)
                        
                        # Only include nodes with meaningful relevance (>0.1)
                        if relevance_score > 0.1:
                            node['relevance_score'] = relevance_score
                            # Boost score for insights vs metrics for better storytelling
                            if node['type'] == 'insight':
                                node['relevance_score'] *= 1.2
                            audience_nodes.append(node)
                    except (json.JSONDecodeError, KeyError):
                        continue
                
                if not audience_nodes:
                    return {'audience': audience, 'nodes': [], 'edges': [], 'total_nodes': 0, 'total_edges': 0}
                
                # Sort by relevance and confidence, then limit for focused view
                audience_nodes.sort(key=lambda x: (x['relevance_score'], x['confidence']), reverse=True)
                focused_nodes = audience_nodes[:limit]
                
                # Create a more connected subgraph by expanding to include related nodes
                focused_node_ids = [node['id'] for node in focused_nodes]
                
                # Find additional highly connected nodes that connect to our focused nodes
                expansion_query = """
                MATCH (focused:Node)-[r:RELATES_TO]-(connected:Node)
                WHERE focused.id IN $focused_ids 
                  AND NOT connected.id IN $focused_ids
                  AND r.weight >= 0.4
                WITH connected, count(r) as connection_count, avg(r.weight) as avg_weight
                ORDER BY connection_count DESC, avg_weight DESC
                LIMIT 10
                RETURN connected.id as id, connected.type as type, connected.content as content,
                       connected.source as source, connected.confidence as confidence, 
                       connected.tags as tags, connected.audience_relevance_json as audience_relevance_json,
                       connected.value as value, connection_count, avg_weight
                """
                
                expansion_nodes = session.run(expansion_query, {
                    'focused_ids': focused_node_ids
                }).data()
                
                # Add expansion nodes with connection info
                for exp_node in expansion_nodes:
                    exp_node['relevance_score'] = 0.3  # Lower relevance for expansion nodes
                    exp_node['is_expansion'] = True
                    focused_nodes.append(exp_node)
                
                all_node_ids = [node['id'] for node in focused_nodes]
                
                # Get edges with better filtering for meaningful connections
                edges_query = """
                MATCH (source:Node)-[r:RELATES_TO]-(target:Node)
                WHERE source.id IN $node_ids AND target.id IN $node_ids
                  AND r.weight >= 0.35
                WITH source, target, r
                ORDER BY r.weight DESC
                RETURN source.id as source_id, target.id as target_id,
                       r.weight as weight, r.relationship_type as relationship_type,
                       r.confidence as confidence, r.semantic_similarity as semantic_similarity,
                       r.metadata_json as metadata_json
                LIMIT 100
                """
                
                edges = session.run(edges_query, {'node_ids': all_node_ids}).data()
                
                # Add audience-specific metadata
                result = {
                    'audience': audience,
                    'nodes': focused_nodes,
                    'edges': edges,
                    'total_nodes': len(focused_nodes),
                    'total_edges': len(edges),
                    'focus_metadata': {
                        'original_relevant_nodes': len(audience_nodes),
                        'focused_nodes': len([n for n in focused_nodes if not n.get('is_expansion', False)]),
                        'expansion_nodes': len([n for n in focused_nodes if n.get('is_expansion', False)]),
                        'avg_relevance': sum(n['relevance_score'] for n in focused_nodes) / len(focused_nodes) if focused_nodes else 0,
                        'audience_insights': self._get_audience_insights(audience, focused_nodes)
                    }
                }
                
                logger.info(f"✅ Generated {audience} graph: {len(focused_nodes)} nodes, {len(edges)} edges")
                return result
                
            except Exception as e:
                logger.error(f"Audience graph failed for {audience}: {e}")
                return {'audience': audience, 'nodes': [], 'edges': [], 'total_nodes': 0, 'total_edges': 0}
    
    def _get_audience_insights(self, audience: str, nodes: List[Dict]) -> Dict:
        """Generate audience-specific insights from the nodes"""
        insights = {
            'top_categories': {},
            'key_metrics': [],
            'data_sources': {},
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        try:
            for node in nodes:
                # Count categories from tags
                if 'tags' in node and node['tags']:
                    for tag in node['tags']:
                        if tag.startswith('category_'):
                            category = tag.replace('category_', '')
                            insights['top_categories'][category] = insights['top_categories'].get(category, 0) + 1
                
                # Collect high-value metrics/insights
                if node.get('relevance_score', 0) > 0.6 and len(insights['key_metrics']) < 5:
                    insights['key_metrics'].append({
                        'content': node['content'],
                        'relevance': node['relevance_score'],
                        'type': node['type']
                    })
                
                # Count data sources
                source = node.get('source', 'unknown')
                insights['data_sources'][source] = insights['data_sources'].get(source, 0) + 1
                
                # Confidence distribution
                confidence = node.get('confidence', 0)
                if confidence >= 0.8:
                    insights['confidence_distribution']['high'] += 1
                elif confidence >= 0.6:
                    insights['confidence_distribution']['medium'] += 1
                else:
                    insights['confidence_distribution']['low'] += 1
            
            # Sort categories and sources by count
            insights['top_categories'] = dict(sorted(insights['top_categories'].items(), 
                                                   key=lambda x: x[1], reverse=True)[:3])
            insights['data_sources'] = dict(sorted(insights['data_sources'].items(), 
                                                 key=lambda x: x[1], reverse=True)[:5])
            
        except Exception as e:
            logger.warning(f"Failed to generate insights for {audience}: {e}")
        
        return insights
    
    def get_analytics_summary(self) -> Dict:
        """Get advanced analytics similar to Linkurious insights"""
        with self.driver.session() as session:
            # Most connected nodes (high centrality)
            centrality_query = """
            MATCH (n:Node)
            OPTIONAL MATCH (n)-[r:RELATES_TO]-()
            WITH n, count(r) as degree
            ORDER BY degree DESC
            LIMIT 10
            RETURN collect({
                id: n.id,
                content: n.content,
                type: n.type,
                degree: degree
            }) as top_connected_nodes
            """
            
            # Strongest relationships
            strong_relationships = """
            MATCH (source:Node)-[r:RELATES_TO]->(target:Node)
            WHERE r.weight >= 0.7
            RETURN collect({
                source_content: source.content,
                target_content: target.content,
                weight: r.weight,
                relationship_type: r.relationship_type
            }) as strong_relationships
            ORDER BY r.weight DESC
            LIMIT 20
            """
            
            # Tag distribution
            tag_distribution = """
            MATCH (n:Node)
            UNWIND n.tags as tag
            RETURN tag, count(*) as frequency
            ORDER BY frequency DESC
            LIMIT 15
            """
            
            centrality = session.run(centrality_query).single()['top_connected_nodes']
            relationships = session.run(strong_relationships).single()['strong_relationships']
            tags = session.run(tag_distribution).data()
            
            return {
                'top_connected_nodes': centrality,
                'strongest_relationships': relationships,
                'tag_distribution': tags,
                'generated_at': datetime.now().isoformat()
            }

# Usage example and initialization
def initialize_neo4j_graph(nodes_file: str, edges_file: str) -> Neo4jGraphClient:
    """Initialize Neo4j with graph data"""
    client = Neo4jGraphClient()
    
    try:
        # Setup database
        client.create_constraints()
        
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
    # Example usage
    client = initialize_neo4j_graph(
        'nodes/flowmetrics_nodes.json',
        'edges/flowmetrics_edges.json'
    )
    
    # Get overview
    overview = client.get_graph_overview()
    print(json.dumps(overview, indent=2))
    
    # Search example
    results = client.search_nodes("user growth")
    print(f"Found {len(results)} matching nodes")
    
    client.close() 