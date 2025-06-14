"""
FlowMetrics Semantic Graph Builder - Clean Version
Uses machine learning to create meaningful relationships between data points
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import networkx as nx
import os
from datetime import datetime
import uuid

@dataclass
class GraphNode:
    """Node in the semantic graph"""
    id: str
    type: str  # "metric", "insight", "event", "trend"
    content: str
    value: Any
    timestamp: str
    confidence: float
    source: str
    tags: List[str]
    audience_relevance: Dict[str, float]
    embedding: List[float]
    metadata: Dict[str, Any]

@dataclass
class GraphEdge:
    """Edge connecting two nodes"""
    source_id: str
    target_id: str
    relationship_type: str
    weight: float
    confidence: float
    semantic_similarity: float
    metadata: Dict[str, Any]

class FlowMetricsGraphBuilder:
    """Build semantic graph from FlowMetrics data using ML"""
    
    def __init__(self):
        print("🤖 Initializing FlowMetrics Graph Builder...")
        
        # Initialize sentence transformer for semantic embeddings
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Graph storage
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.nx_graph = nx.Graph()
        
        # Audience definitions for relevance scoring
        self.audiences = {
            "investors": {
                "keywords": ["revenue", "growth", "arr", "mrr", "churn", "funding", "runway"],
                "interests": ["financial_metrics", "growth_trajectory", "market_position"]
            },
            "customers": {
                "keywords": ["feature", "update", "integration", "dashboard", "support"],
                "interests": ["product_updates", "feature_releases", "user_experience"]
            },
            "internal_team": {
                "keywords": ["performance", "velocity", "sprint", "kpi", "productivity"],
                "interests": ["team_performance", "operational_metrics", "strategic_initiatives"]
            },
            "developer_community": {
                "keywords": ["api", "integration", "documentation", "technical"],
                "interests": ["technical_updates", "integration_capabilities"]
            }
        }
    
    def load_flowmetrics_data(self) -> List[Dict]:
        """Load all FlowMetrics data files"""
        print("📊 Loading FlowMetrics dataset...")
        
        data_files = [
            "data/product_analytics/daily_active_users.json",
            "data/product_analytics/feature_adoption.json",
            "data/revenue_metrics/monthly_recurring_revenue.json",
            "data/customer_feedback/support_tickets.json",
            "data/market_intelligence/competitor_analysis.json",
            "data/social_listening/brand_mentions.json",
            "data/team_metrics/internal_kpis.json"
        ]
        
        all_data = []
        for file_path in data_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['_file_source'] = file_path
                    all_data.append(data)
                    print(f"✅ Loaded {file_path}")
        
        return all_data
    
    def calculate_audience_relevance(self, content: str, tags: List[str]) -> Dict[str, float]:
        """Calculate relevance scores for each audience using keyword matching"""
        relevance_scores = {}
        
        # Combine content and tags for analysis
        text_for_analysis = f"{content} {' '.join(tags)}"
        content_lower = text_for_analysis.lower()
        
        for audience, profile in self.audiences.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in profile['keywords'] if keyword in content_lower)
            keyword_score = min(keyword_matches / len(profile['keywords']), 1.0)
            
            # Tag relevance
            tag_relevance = 0.0
            for tag in tags:
                if any(interest in tag for interest in profile['interests']):
                    tag_relevance += 0.2
            
            # Combine scores
            score = (keyword_score * 0.7) + (min(tag_relevance, 1.0) * 0.3)
            relevance_scores[audience] = round(score, 3)
        
        return relevance_scores
    
    def create_graph_nodes(self, data_points: List[Dict]) -> None:
        """Convert data points to graph nodes with embeddings"""
        print("🧠 Creating graph nodes with semantic embeddings...")
        
        # Extract content for batch embedding
        contents = [point['content'] for point in data_points]
        
        # Generate embeddings in batch for efficiency
        print("🔄 Generating semantic embeddings...")
        embeddings = self.sentence_model.encode(contents)
        
        for i, point in enumerate(data_points):
            node_id = str(uuid.uuid4())
            
            # Calculate audience relevance
            audience_relevance = self.calculate_audience_relevance(
                point['content'], 
                point['tags']
            )
            
            # Create node
            node = GraphNode(
                id=node_id,
                type=point['type'],
                content=point['content'],
                value=point['value'],
                timestamp=point['timestamp'],
                confidence=point['confidence'],
                source=point['source'],
                tags=point['tags'],
                audience_relevance=audience_relevance,
                embedding=embeddings[i].tolist(),
                metadata=point['metadata']
            )
            
            self.nodes[node_id] = node
            # Add simplified node attributes for NetworkX compatibility
            self.nx_graph.add_node(
                node_id, 
                type=node.type,
                content=node.content[:100],  # Truncate for compatibility
                source=node.source,
                confidence=str(node.confidence),
                tags=",".join(node.tags[:3])  # Limit tags for compatibility
            )
        
        print(f"✅ Created {len(self.nodes)} graph nodes")
    
    def calculate_semantic_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        return float(cosine_similarity([embedding1], [embedding2])[0][0])
    
    def create_semantic_edges(self, similarity_threshold: float = 0.3) -> None:
        """Create edges based on semantic similarity and logical relationships"""
        print("🔗 Creating semantic edges...")
        
        node_list = list(self.nodes.values())
        edge_count = 0
        
        for i, node1 in enumerate(node_list):
            for j, node2 in enumerate(node_list[i+1:], i+1):
                
                # Calculate semantic similarity
                similarity = self.calculate_semantic_similarity(
                    node1.embedding, 
                    node2.embedding
                )
                
                # Determine relationship type and weight
                relationship_type, weight, confidence = self._analyze_relationship(
                    node1, node2, similarity
                )
                
                # Create edge if similarity exceeds threshold
                if similarity > similarity_threshold and weight > 0:
                    edge = GraphEdge(
                        source_id=node1.id,
                        target_id=node2.id,
                        relationship_type=relationship_type,
                        weight=weight,
                        confidence=confidence,
                        semantic_similarity=similarity,
                        metadata={
                            "similarity_score": similarity,
                            "source_types": f"{node1.type}-{node2.type}",
                            "shared_tags": list(set(node1.tags) & set(node2.tags))
                        }
                    )
                    
                    self.edges.append(edge)
                    self.nx_graph.add_edge(
                        node1.id, 
                        node2.id, 
                        weight=weight,
                        relationship=relationship_type,
                        similarity=similarity
                    )
                    edge_count += 1
        
        print(f"✅ Created {edge_count} semantic edges")
    
    def _analyze_relationship(self, node1: GraphNode, node2: GraphNode, similarity: float) -> Tuple[str, float, float]:
        """Analyze the relationship between two nodes"""
        
        # Tag overlap analysis
        shared_tags = set(node1.tags) & set(node2.tags)
        tag_overlap = len(shared_tags) / max(len(node1.tags), len(node2.tags), 1)
        
        # Type-based relationship rules
        relationship_type = "relevance"  # default
        base_weight = similarity
        confidence = 0.7
        
        # Causal relationships
        if (node1.type == "insight" and node2.type == "metric" or 
            node2.type == "insight" and node1.type == "metric"):
            if any(tag in shared_tags for tag in ["growth", "improvement", "performance"]):
                relationship_type = "causality"
                base_weight = min(base_weight * 1.3, 1.0)
                confidence = 0.8
        
        # Influence relationships
        if (node1.type == "event" and node2.type in ["metric", "insight"] or
            node2.type == "event" and node1.type in ["metric", "insight"]):
            relationship_type = "influence"
            base_weight = min(base_weight * 1.2, 1.0)
            confidence = 0.75
        
        # Boost weight based on tag overlap
        final_weight = min(base_weight * (1 + tag_overlap * 0.5), 1.0)
        
        return relationship_type, final_weight, confidence
    
    def save_graph(self) -> None:
        """Save the graph in multiple formats"""
        print("💾 Saving graph data...")
        
        # Save nodes
        nodes_data = {
            "metadata": {
                "total_nodes": len(self.nodes),
                "node_types": list(set(node.type for node in self.nodes.values())),
                "creation_timestamp": datetime.now().isoformat()
            },
            "nodes": [asdict(node) for node in self.nodes.values()]
        }
        
        with open("graphs/nodes/flowmetrics_nodes.json", "w") as f:
            json.dump(nodes_data, f, indent=2)
        
        # Save edges
        edges_data = {
            "metadata": {
                "total_edges": len(self.edges),
                "relationship_types": list(set(edge.relationship_type for edge in self.edges)),
                "creation_timestamp": datetime.now().isoformat()
            },
            "edges": [asdict(edge) for edge in self.edges]
        }
        
        with open("graphs/edges/flowmetrics_edges.json", "w") as f:
            json.dump(edges_data, f, indent=2)
        
        # Save as simple edge list instead of GEXF
        nx.write_edgelist(self.nx_graph, "graphs/processed/flowmetrics_graph.edgelist")
        
        # Create summary
        summary = {
            "graph_summary": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": {},
                "relationship_types": {},
                "audience_coverage": {},
                "source_distribution": {}
            }
        }
        
        # Calculate summaries
        for node in self.nodes.values():
            summary["graph_summary"]["node_types"][node.type] = \
                summary["graph_summary"]["node_types"].get(node.type, 0) + 1
            summary["graph_summary"]["source_distribution"][node.source] = \
                summary["graph_summary"]["source_distribution"].get(node.source, 0) + 1
        
        for edge in self.edges:
            summary["graph_summary"]["relationship_types"][edge.relationship_type] = \
                summary["graph_summary"]["relationship_types"].get(edge.relationship_type, 0) + 1
        
        # Audience coverage analysis
        for audience in self.audiences.keys():
            relevant_nodes = [n for n in self.nodes.values() if n.audience_relevance.get(audience, 0) > 0.3]
            summary["graph_summary"]["audience_coverage"][audience] = len(relevant_nodes)
        
        with open("graphs/processed/graph_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("✅ Graph saved successfully!")
        print(f"   📊 Nodes: {len(self.nodes)}")
        print(f"   🔗 Edges: {len(self.edges)}")
        print(f"   📁 Files: graphs/nodes/, graphs/edges/, graphs/processed/") 