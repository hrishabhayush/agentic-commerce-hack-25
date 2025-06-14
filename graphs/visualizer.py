#!/usr/bin/env python3
"""
Comprehensive Graph Visualization System for Agentic Commerce
Provides multiple visualization types for internal teams to understand semantic graph structure
"""

import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from collections import defaultdict, Counter
import textwrap

class GraphVisualizer:
    def __init__(self, nodes_file, edges_file, summary_file):
        """Initialize the visualizer with graph data files"""
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        self.summary_file = summary_file
        
        # Load data
        self.nodes_data = self.load_json(nodes_file)
        self.edges_data = self.load_json(edges_file)
        self.summary_data = self.load_json(summary_file)
        
        # Create NetworkX graph
        self.graph = self.build_networkx_graph()
        
        # Process data for visualizations
        self.nodes_df = self.create_nodes_dataframe()
        self.edges_df = self.create_edges_dataframe()
        
    def load_json(self, filepath):
        """Load JSON data from file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}
    
    def build_networkx_graph(self):
        """Build NetworkX graph from our data"""
        G = nx.Graph()
        
        # Add nodes
        for node in self.nodes_data.get('nodes', []):
            G.add_node(
                node['id'],
                type=node['type'],
                content=node['content'],
                source=node['source'],
                confidence=node['confidence'],
                tags=node['tags'],
                value=node.get('value', 0)
            )
        
        # Add edges
        for edge in self.edges_data.get('edges', []):
            G.add_edge(
                edge['source_id'],
                edge['target_id'],
                weight=edge['weight'],
                relationship_type=edge['relationship_type'],
                similarity=edge['semantic_similarity']
            )
        
        return G
    
    def create_nodes_dataframe(self):
        """Create pandas DataFrame for nodes analysis"""
        nodes_list = []
        for node in self.nodes_data.get('nodes', []):
            node_data = {
                'id': node['id'],
                'type': node['type'],
                'content': node['content'][:100] + '...' if len(node['content']) > 100 else node['content'],
                'source': node['source'],
                'confidence': node['confidence'],
                'value': node.get('value', 0),
                'tag_count': len(node['tags']),
                'tags': ', '.join(node['tags'])
            }
            nodes_list.append(node_data)
        
        return pd.DataFrame(nodes_list)
    
    def create_edges_dataframe(self):
        """Create pandas DataFrame for edges analysis"""
        edges_list = []
        for edge in self.edges_data.get('edges', []):
            edge_data = {
                'source': edge['source_id'],
                'target': edge['target_id'],
                'weight': edge['weight'],
                'similarity': edge['semantic_similarity'],
                'relationship_type': edge['relationship_type'],
                'confidence': edge['confidence']
            }
            edges_list.append(edge_data)
        
        return pd.DataFrame(edges_list)
    
    def create_interactive_network(self):
        """Create interactive network visualization using Plotly"""
        # Get node positions using spring layout
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Get edge data
            edge_data = self.graph[edge[0]][edge[1]]
            edge_info.append(f"Weight: {edge_data['weight']:.3f}<br>Similarity: {edge_data['similarity']:.3f}")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces by type
        node_traces = {}
        colors = {'metric': '#FF6B6B', 'insight': '#4ECDC4'}
        
        for node_type in ['metric', 'insight']:
            node_x = []
            node_y = []
            node_text = []
            node_info = []
            node_sizes = []
            
            for node in self.graph.nodes():
                if self.graph.nodes[node]['type'] == node_type:
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    
                    # Node info for hover
                    node_data = self.graph.nodes[node]
                    wrapped_content = '<br>'.join(textwrap.wrap(node_data['content'], width=50))
                    info = (f"Type: {node_data['type']}<br>"
                           f"Source: {node_data['source']}<br>"
                           f"Confidence: {node_data['confidence']}<br>"
                           f"Content: {wrapped_content}<br>"
                           f"Tags: {', '.join(node_data['tags'])}")
                    node_info.append(info)
                    node_text.append(f"{node_data['source']}")
                    
                    # Size based on degree centrality
                    degree = self.graph.degree(node)
                    node_sizes.append(10 + degree * 3)
            
            node_traces[node_type] = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                hovertext=node_info,
                marker=dict(
                    size=node_sizes,
                    color=colors[node_type],
                    line=dict(width=2, color='white')
                ),
                name=f"{node_type.title()} Nodes"
            )
        
        # Create the figure
        fig = go.Figure(data=[edge_trace] + list(node_traces.values()),
                       layout=go.Layout(
                           title=dict(text="FlowMetrics Semantic Knowledge Graph", font=dict(size=16)),
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Node size represents connection degree. Hover for details.",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color="#888", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='white'
                       ))
        
        return fig
    
    def create_analytics_dashboard(self):
        """Create comprehensive analytics dashboard"""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Node Type Distribution', 'Source Distribution',
                          'Connection Strength Distribution', 'Node Confidence Levels',
                          'Tag Frequency Analysis', 'Network Metrics Summary'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "box"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )
        
        # 1. Node Type Distribution (Pie Chart)
        type_counts = self.nodes_df['type'].value_counts()
        fig.add_trace(
            go.Pie(labels=type_counts.index, values=type_counts.values, name="Node Types"),
            row=1, col=1
        )
        
        # 2. Source Distribution (Bar Chart)
        source_counts = self.nodes_df['source'].value_counts()
        fig.add_trace(
            go.Bar(x=source_counts.index, y=source_counts.values, name="Sources"),
            row=1, col=2
        )
        
        # 3. Connection Strength Distribution (Histogram)
        fig.add_trace(
            go.Histogram(x=self.edges_df['weight'], name="Edge Weights", nbinsx=20),
            row=2, col=1
        )
        
        # 4. Node Confidence Levels (Box Plot)
        confidence_by_type = []
        types = []
        for node_type in self.nodes_df['type'].unique():
            confidence_by_type.extend(self.nodes_df[self.nodes_df['type'] == node_type]['confidence'].tolist())
            types.extend([node_type] * len(self.nodes_df[self.nodes_df['type'] == node_type]))
        
        fig.add_trace(
            go.Box(y=confidence_by_type, x=types, name="Confidence"),
            row=2, col=2
        )
        
        # 5. Tag Frequency Analysis
        all_tags = []
        for node in self.nodes_data.get('nodes', []):
            all_tags.extend(node['tags'])
        tag_counts = Counter(all_tags).most_common(10)
        
        fig.add_trace(
            go.Bar(x=[tag[1] for tag in tag_counts], 
                  y=[tag[0] for tag in tag_counts], 
                  orientation='h', name="Top Tags"),
            row=3, col=1
        )
        
        # 6. Network Metrics Summary (Table)
        metrics = {
            'Metric': ['Total Nodes', 'Total Edges', 'Average Degree', 'Density', 
                      'Connected Components', 'Average Clustering', 'Diameter'],
            'Value': [
                self.graph.number_of_nodes(),
                self.graph.number_of_edges(),
                f"{2 * self.graph.number_of_edges() / self.graph.number_of_nodes():.2f}",
                f"{nx.density(self.graph):.3f}",
                nx.number_connected_components(self.graph),
                f"{nx.average_clustering(self.graph):.3f}",
                nx.diameter(self.graph) if nx.is_connected(self.graph) else "N/A (disconnected)"
            ]
        }
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value']),
                cells=dict(values=[metrics['Metric'], metrics['Value']])
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="FlowMetrics Graph Analytics Dashboard",
            showlegend=False
        )
        
        return fig
    
    def create_relationship_analysis(self):
        """Create detailed relationship strength visualization"""
        # Calculate node centrality measures
        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)
        closeness_centrality = nx.closeness_centrality(self.graph)
        
        # Create centrality DataFrame
        centrality_data = []
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            centrality_data.append({
                'node_id': node_id,
                'content': node_data['content'][:50] + '...',
                'type': node_data['type'],
                'source': node_data['source'],
                'degree_centrality': degree_centrality[node_id],
                'betweenness_centrality': betweenness_centrality[node_id],
                'closeness_centrality': closeness_centrality[node_id]
            })
        
        centrality_df = pd.DataFrame(centrality_data)
        
        # Create bubble chart for centrality analysis
        fig = px.scatter(
            centrality_df,
            x='degree_centrality',
            y='betweenness_centrality',
            size='closeness_centrality',
            color='type',
            hover_data=['content', 'source'],
            title='Node Centrality Analysis (size = closeness centrality)',
            labels={
                'degree_centrality': 'Degree Centrality (Connectivity)',
                'betweenness_centrality': 'Betweenness Centrality (Bridge Role)'
            }
        )
        
        return fig
    
    def generate_insights_report(self):
        """Generate textual insights about the graph"""
        insights = []
        
        # Basic stats
        insights.append(f"📊 **Graph Overview:**")
        insights.append(f"- Total nodes: {self.graph.number_of_nodes()}")
        insights.append(f"- Total edges: {self.graph.number_of_edges()}")
        insights.append(f"- Graph density: {nx.density(self.graph):.3f}")
        insights.append("")
        
        # Node analysis
        type_counts = self.nodes_df['type'].value_counts()
        insights.append(f"🎯 **Node Composition:**")
        for node_type, count in type_counts.items():
            percentage = (count / len(self.nodes_df)) * 100
            insights.append(f"- {node_type.title()}: {count} nodes ({percentage:.1f}%)")
        insights.append("")
        
        # Source analysis
        source_counts = self.nodes_df['source'].value_counts()
        insights.append(f"📡 **Data Sources:**")
        for source, count in source_counts.items():
            insights.append(f"- {source}: {count} nodes")
        insights.append("")
        
        # Centrality insights
        degree_centrality = nx.degree_centrality(self.graph)
        most_connected = max(degree_centrality.items(), key=lambda x: x[1])
        most_connected_node = self.graph.nodes[most_connected[0]]
        
        insights.append(f"🔗 **Key Connections:**")
        insights.append(f"- Most connected node: {most_connected_node['content'][:100]}...")
        insights.append(f"- Connection score: {most_connected[1]:.3f}")
        insights.append("")
        
        # Edge strength analysis
        avg_weight = self.edges_df['weight'].mean()
        strong_edges = len(self.edges_df[self.edges_df['weight'] > avg_weight])
        insights.append(f"💪 **Relationship Strength:**")
        insights.append(f"- Average edge weight: {avg_weight:.3f}")
        insights.append(f"- Strong connections (above average): {strong_edges}/{len(self.edges_df)}")
        
        return "\n".join(insights)
    
    def save_visualizations(self, output_dir="visualizations"):
        """Save all visualizations to HTML files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Interactive Network
        network_fig = self.create_interactive_network()
        network_fig.write_html(f"{output_dir}/network_graph.html")
        
        # Analytics Dashboard
        dashboard_fig = self.create_analytics_dashboard()
        dashboard_fig.write_html(f"{output_dir}/analytics_dashboard.html")
        
        # Relationship Analysis
        relationship_fig = self.create_relationship_analysis()
        relationship_fig.write_html(f"{output_dir}/relationship_analysis.html")
        
        # Save insights report
        insights = self.generate_insights_report()
        with open(f"{output_dir}/insights_report.md", 'w') as f:
            f.write("# FlowMetrics Semantic Graph Analysis Report\n\n")
            f.write(insights)
        
        print(f"✅ Visualizations saved to {output_dir}/")
        print(f"   📊 Network Graph: {output_dir}/network_graph.html")
        print(f"   📈 Analytics Dashboard: {output_dir}/analytics_dashboard.html")
        print(f"   🔍 Relationship Analysis: {output_dir}/relationship_analysis.html")
        print(f"   📝 Insights Report: {output_dir}/insights_report.md")


def main():
    """Main function to run the visualization system"""
    # File paths
    nodes_file = "nodes/flowmetrics_nodes.json"
    edges_file = "edges/flowmetrics_edges.json" 
    summary_file = "processed/graph_summary.json"
    
    try:
        # Initialize visualizer
        print("🚀 Initializing Graph Visualization System...")
        visualizer = GraphVisualizer(nodes_file, edges_file, summary_file)
        
        # Generate and save all visualizations
        print("📊 Generating visualizations...")
        visualizer.save_visualizations()
        
        # Print insights
        print("\n" + "="*60)
        print("🔍 GRAPH INSIGHTS SUMMARY")
        print("="*60)
        print(visualizer.generate_insights_report())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main() 