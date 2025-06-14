#!/usr/bin/env python3
"""
Main script to generate FlowMetrics semantic graph
Usage: python graphs/generate_graph.py
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.graph_builder_clean import FlowMetricsGraphBuilder, GraphNode, GraphEdge
from graphs.data_extractor import FlowMetricsDataExtractor

def main():
    """Main execution function"""
    print("🚀 Starting FlowMetrics Semantic Graph Generation")
    print("=" * 60)
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        builder = FlowMetricsGraphBuilder()
        extractor = FlowMetricsDataExtractor()
        
        # Load FlowMetrics data
        data = builder.load_flowmetrics_data()
        if not data:
            print("❌ No data found! Make sure data files exist.")
            return
        
        # Extract data points
        data_points = extractor.extract_data_points(data)
        if not data_points:
            print("❌ No data points extracted!")
            return
        
        # Create graph nodes with embeddings
        print("🧠 Creating semantic graph...")
        builder.create_graph_nodes(data_points)
        
        # Create edges based on semantic similarity
        print("🔗 Creating relationships...")
        builder.create_semantic_edges(similarity_threshold=0.25)
        
        # Save the graph
        print("💾 Saving graph...")
        builder.save_graph()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 Graph Generation Complete!")
        print(f"📊 Total Nodes: {len(builder.nodes)}")
        print(f"🔗 Total Edges: {len(builder.edges)}")
        print("📁 Output Files:")
        print("   - graphs/nodes/flowmetrics_nodes.json")
        print("   - graphs/edges/flowmetrics_edges.json") 
        print("   - graphs/processed/flowmetrics_graph.gexf")
        print("   - graphs/processed/graph_summary.json")
        
        # Show node type breakdown
        node_types = {}
        for node in builder.nodes.values():
            node_types[node.type] = node_types.get(node.type, 0) + 1
        
        print("\n📈 Node Types:")
        for node_type, count in node_types.items():
            print(f"   {node_type}: {count}")
        
        # Show relationship breakdown
        relationship_types = {}
        for edge in builder.edges:
            relationship_types[edge.relationship_type] = relationship_types.get(edge.relationship_type, 0) + 1
        
        print("\n🔗 Relationship Types:")
        for rel_type, count in relationship_types.items():
            print(f"   {rel_type}: {count}")
        
        print("\n✅ Ready for content generation!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 