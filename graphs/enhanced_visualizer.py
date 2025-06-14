#!/usr/bin/env python3
"""
Enhanced Graph Visualizer for Agentic Commerce
Provides intelligent filtering, audience-specific views, and actionable insights
"""

import json
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from collections import defaultdict, Counter
import textwrap
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

@dataclass
class InsightCluster:
    """Represents a cluster of related insights"""
    id: str
    name: str
    description: str
    audience: str
    priority: str  # high, medium, low
    nodes: List[str]
    key_metrics: List[str]
    actionable_insights: List[str]

class EnhancedGraphVisualizer:
    def __init__(self, nodes_file: str, edges_file: str):
        """Initialize enhanced visualizer with intelligent filtering"""
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        
        # Audience definitions with improved keyword matching
        self.audiences = {
            "investors": {
                "keywords": ["revenue", "growth", "arr", "mrr", "churn", "market", "funding", "recurring"],
                "color": "#FF6B6B"
            },
            "customers": {
                "keywords": ["feature", "update", "experience", "satisfaction", "support", "adoption"],
                "color": "#4ECDC4"
            },
            "internal_team": {
                "keywords": ["performance", "productivity", "team", "velocity", "kpi", "active"],
                "color": "#45B7D1"
            },
            "developer_community": {
                "keywords": ["api", "integration", "technical", "documentation"],
                "color": "#96CEB4"
            }
        }
        
        # Load and process data
        self.nodes_data = self.load_json(nodes_file)
        self.edges_data = self.load_json(edges_file)
        
        # Create filtered graph
        self.graph = self.build_filtered_graph()
        
        # Generate insight clusters
        self.clusters = self.generate_insight_clusters()

    def load_json(self, filepath: str) -> dict:
        """Load JSON data from file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}

    def get_primary_audience(self, audience_relevance: Dict[str, float]) -> str:
        """Get the primary audience for a node with enhanced logic"""
        if not audience_relevance or all(score == 0.0 for score in audience_relevance.values()):
            return "general"
        
        max_score = max(audience_relevance.values())
        if max_score < 0.1:  # Very low relevance threshold
            return "general"
            
        return max(audience_relevance.items(), key=lambda x: x[1])[0]

    def enhance_audience_relevance(self, node: dict) -> dict:
        """Enhance audience relevance calculation based on content and tags"""
        content_lower = node['content'].lower()
        tags_lower = [tag.lower() for tag in node['tags']]
        all_text = content_lower + " " + " ".join(tags_lower)
        
        enhanced_relevance = {}
        
        for audience, profile in self.audiences.items():
            score = 0.0
            
            # Keyword matching in content and tags
            keyword_matches = sum(1 for keyword in profile['keywords'] if keyword in all_text)
            if keyword_matches > 0:
                score = min(keyword_matches / len(profile['keywords']) * 2, 1.0)
            
            # Boost based on specific patterns
            if audience == "investors":
                if any(word in all_text for word in ["growth", "revenue", "recurring", "users"]):
                    score = max(score, 0.8)
            elif audience == "customers":
                if any(word in all_text for word in ["feature", "adoption", "satisfaction"]):
                    score = max(score, 0.7)
            elif audience == "internal_team":
                if any(word in all_text for word in ["active", "performance", "kpi"]):
                    score = max(score, 0.6)
            
            enhanced_relevance[audience] = round(score, 3)
        
        return enhanced_relevance

    def calculate_node_importance(self, node: dict) -> str:
        """Calculate node importance based on various factors"""
        score = 0
        
        # Confidence weight
        score += node['confidence'] * 2
        
        # Enhanced audience relevance
        enhanced_rel = self.enhance_audience_relevance(node)
        max_relevance = max(enhanced_rel.values())
        score += max_relevance * 3
        
        # Value weight (if numerical and significant)
        value = node.get('value', 0)
        if isinstance(value, (int, float)) and abs(value) > 0:
            if abs(value) >= 10:  # Significant percentage or count
                score += 2
            elif abs(value) >= 1:
                score += 1
        
        # Important tag bonus
        important_tags = {'revenue', 'growth', 'churn', 'users', 'active', 'recurring'}
        tag_matches = len(set([t.lower() for t in node['tags']]).intersection(important_tags))
        score += tag_matches * 0.5
        
        if score >= 4:
            return "high"
        elif score >= 2.5:
            return "medium"
        else:
            return "low"

    def build_filtered_graph(self) -> nx.Graph:
        """Build NetworkX graph with intelligent edge filtering"""
        G = nx.Graph()
        
        # Add nodes with enhanced attributes
        for node in self.nodes_data.get('nodes', []):
            # Enhance audience relevance
            enhanced_relevance = self.enhance_audience_relevance(node)
            primary_audience = self.get_primary_audience(enhanced_relevance)
            importance = self.calculate_node_importance(node)
            
            G.add_node(
                node['id'],
                type=node['type'],
                content=node['content'],
                source=node['source'],
                confidence=node['confidence'],
                tags=node['tags'],
                value=node.get('value', 0),
                audience_relevance=enhanced_relevance,
                primary_audience=primary_audience,
                importance=importance
            )
        
        # Add only meaningful edges
        filtered_edges = self.filter_meaningful_edges()
        for edge in filtered_edges:
            G.add_edge(
                edge['source_id'],
                edge['target_id'],
                weight=edge['weight'],
                relationship_type=edge['relationship_type'],
                similarity=edge['semantic_similarity'],
                strength=self.categorize_edge_strength(edge['weight'])
            )
        
        return G

    def filter_meaningful_edges(self) -> List[dict]:
        """Filter edges to show only meaningful relationships"""
        edges = self.edges_data.get('edges', [])
        filtered = []
        
        for edge in edges:
            # More lenient similarity threshold but still meaningful
            if edge['semantic_similarity'] < 0.3:
                continue
                
            # Weight threshold
            if edge['weight'] < 0.35:
                continue
                
            # Enhanced relationship type
            enhanced_type = self.enhance_relationship_type(edge)
            edge['relationship_type'] = enhanced_type
            
            filtered.append(edge)
        
        print(f"Filtered edges: {len(filtered)} from {len(edges)} total")
        return filtered

    def enhance_relationship_type(self, edge: dict) -> str:
        """Enhance relationship type based on node content and metadata"""
        metadata = edge.get('metadata', {})
        shared_tags = metadata.get('shared_tags', [])
        source_types = metadata.get('source_types', '')
        
        # More nuanced relationship typing
        if any(tag in ['growth', 'revenue', 'users', 'recurring'] for tag in shared_tags):
            return "business_growth"
        elif any(tag in ['engagement', 'behavior', 'product', 'active'] for tag in shared_tags):
            return "user_engagement"  
        elif any(tag in ['performance', 'team', 'velocity'] for tag in shared_tags):
            return "operational"
        elif 'metric' in source_types and 'insight' in source_types:
            return "metric_to_insight"
        elif 'metric-metric' in source_types:
            return "metric_correlation"
        else:
            return "contextual_relevance"

    def categorize_edge_strength(self, weight: float) -> str:
        """Categorize edge strength"""
        if weight >= 0.6:
            return "strong"
        elif weight >= 0.45:
            return "medium"
        else:
            return "weak"

    def generate_insight_clusters(self) -> List[InsightCluster]:
        """Generate clusters of related insights for each audience"""
        clusters = []
        
        # Group nodes by primary audience
        audience_groups = defaultdict(list)
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            audience = node_data['primary_audience']
            if audience != 'general':
                audience_groups[audience].append(node_id)
        
        print(f"Audience groups: {dict(audience_groups)}")
        
        # Create clusters for each audience
        for audience, node_ids in audience_groups.items():
            if len(node_ids) < 1:  # Allow single-node clusters
                continue
                
            # For small groups, create one cluster
            if len(node_ids) <= 3:
                cluster = self.create_insight_cluster(audience, 0, node_ids)
                if cluster:
                    clusters.append(cluster)
            else:
                # Find connected components
                subgraph = self.graph.subgraph(node_ids)
                components = list(nx.connected_components(subgraph))
                
                for i, component in enumerate(components):
                    cluster = self.create_insight_cluster(audience, i, list(component))
                    if cluster:
                        clusters.append(cluster)
        
        print(f"Generated {len(clusters)} clusters")
        return clusters

    def create_insight_cluster(self, audience: str, cluster_id: int, node_ids: List[str]) -> InsightCluster:
        """Create an insight cluster from a group of nodes"""
        if not node_ids:
            return None
            
        cluster_nodes = [self.graph.nodes[nid] for nid in node_ids]
        
        # Find common themes
        all_tags = []
        for node in cluster_nodes:
            all_tags.extend([tag.lower() for tag in node['tags']])
        
        common_tags = [tag for tag, count in Counter(all_tags).most_common(3)]
        
        # Generate cluster name
        cluster_name = self.generate_cluster_name(audience, common_tags)
        
        # Separate metrics and insights
        metrics = [node for node in cluster_nodes if node['type'] == 'metric']
        insights = [node for node in cluster_nodes if node['type'] == 'insight']
        
        # Determine priority
        high_importance_nodes = [n for n in cluster_nodes if n['importance'] == 'high']
        if len(high_importance_nodes) >= len(cluster_nodes) * 0.5:
            priority = "high"
        elif len(high_importance_nodes) > 0:
            priority = "medium"
        else:
            priority = "low"
        
        # Generate actionable insights
        actionable_insights = self.generate_actionable_insights(audience, cluster_nodes, common_tags)
        
        return InsightCluster(
            id=f"{audience}_cluster_{cluster_id}",
            name=cluster_name,
            description=f"Insights for {audience} focusing on {', '.join(common_tags[:2])}",
            audience=audience,
            priority=priority,
            nodes=node_ids,
            key_metrics=[f"{m['content'][:50]}... (from {m['source']})" for m in metrics[:3]],
            actionable_insights=actionable_insights
        )

    def generate_cluster_name(self, audience: str, common_tags: List[str]) -> str:
        """Generate meaningful cluster name"""
        if not common_tags:
            return f"{audience.title()} Overview"
        
        primary_theme = common_tags[0]
        audience_prefix = {
            "investors": "Financial",
            "customers": "Product", 
            "internal_team": "Operational",
            "developer_community": "Technical"
        }.get(audience, audience.title())
        
        return f"{audience_prefix} {primary_theme.title()} Analysis"

    def generate_actionable_insights(self, audience: str, nodes: List[dict], themes: List[str]) -> List[str]:
        """Generate actionable insights based on audience and themes"""
        insights = []
        
        # Extract values and trends
        metric_values = [n.get('value', 0) for n in nodes if isinstance(n.get('value'), (int, float))]
        positive_trends = [n for n in nodes if isinstance(n.get('value'), (int, float)) and n.get('value', 0) > 10]
        
        if audience == "investors":
            if 'growth' in themes or 'revenue' in themes:
                insights.append("Highlight growth metrics in investor updates")
            if positive_trends:
                insights.append("Emphasize positive performance trends")
            if 'users' in themes:
                insights.append("Showcase user base expansion")
                
        elif audience == "customers":
            if 'engagement' in themes or 'active' in themes:
                insights.append("Share user engagement improvements in product updates")
            if 'feature' in themes:
                insights.append("Communicate new feature adoption rates")
            insights.append("Consider user feedback for product roadmap")
            
        elif audience == "internal_team":
            if 'performance' in themes:
                insights.append("Review performance metrics for optimization")
            if positive_trends:
                insights.append("Celebrate team achievements in internal communications")
            insights.append("Identify areas for operational improvement")
        
        # Ensure we have at least a few insights
        if len(insights) < 2:
            insights.extend([
                f"Monitor {themes[0] if themes else 'key'} metrics regularly",
                f"Consider {audience} perspective in future analysis"
            ])
        
        return insights[:4]

    def create_audience_filtered_view(self, audience: str = None, min_relevance: float = 0.05):
        """Create audience-specific graph view with lower threshold"""
        if audience and audience in self.audiences:
            relevant_nodes = []
            for node_id in self.graph.nodes():
                node_data = self.graph.nodes[node_id]
                relevance = node_data['audience_relevance'].get(audience, 0)
                if relevance >= min_relevance or node_data['primary_audience'] == audience:
                    relevant_nodes.append(node_id)
            
            subgraph = self.graph.subgraph(relevant_nodes)
            title = f"Knowledge Graph - {audience.title()} Perspective"
        else:
            subgraph = self.graph
            title = "Complete Knowledge Graph - All Audiences"
        
        return self.create_interactive_network(subgraph, title, audience)

    def create_interactive_network(self, graph: nx.Graph, title: str, audience: str = None):
        """Create interactive network visualization with enhanced styling"""
        if len(graph.nodes()) == 0:
            return go.Figure().add_annotation(
                text=f"No relevant data found for {audience or 'this filter'}",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16)
            )
        
        # Generate layout with better spacing
        pos = nx.spring_layout(graph, k=3, iterations=100)
        
        # Create edge traces by relationship type
        edge_traces = self.create_enhanced_edge_traces(graph, pos)
        
        # Create node traces by audience and importance
        node_traces = self.create_enhanced_node_traces(graph, pos, audience)
        
        # Combine all traces
        all_traces = edge_traces + node_traces
        
        # Enhanced layout
        fig = go.Figure(
            data=all_traces,
            layout=go.Layout(
                title=dict(text=title, font=dict(size=20, color='#2C3E50')),
                showlegend=True,
                hovermode='closest',
                margin=dict(b=40, l=20, r=20, t=60),
                annotations=[
                    dict(
                        text="💡 Node size indicates importance | Colors show audience relevance | Hover for details",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.02, y=-0.02,
                        xanchor='left', yanchor='bottom',
                        font=dict(color="#7F8C8D", size=11)
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='#FAFAFA',
                paper_bgcolor='white',
                height=700,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left", 
                    x=1.01
                )
            )
        )
        
        return fig

    def create_enhanced_edge_traces(self, graph: nx.Graph, pos: dict) -> List[go.Scatter]:
        """Create enhanced edge traces with better styling"""
        edge_groups = defaultdict(lambda: {'x': [], 'y': [], 'weights': []})
        
        for edge in graph.edges(data=True):
            rel_type = edge[2].get('relationship_type', 'other')
            weight = edge[2].get('weight', 0.5)
            
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_groups[rel_type]['x'].extend([x0, x1, None])
            edge_groups[rel_type]['y'].extend([y0, y1, None])
            edge_groups[rel_type]['weights'].append(weight)
        
        traces = []
        edge_colors = {
            'business_growth': '#27AE60',
            'user_engagement': '#3498DB',
            'operational': '#E67E22',
            'metric_to_insight': '#8E44AD',
            'metric_correlation': '#F39C12',
            'contextual_relevance': '#95A5A6'
        }
        
        for rel_type, data in edge_groups.items():
            avg_weight = np.mean(data['weights']) if data['weights'] else 0.5
            line_width = max(1, min(4, avg_weight * 6))
            
            traces.append(go.Scatter(
                x=data['x'], y=data['y'],
                line=dict(
                    width=line_width,
                    color=edge_colors.get(rel_type, '#BDC3C7')
                ),
                hoverinfo='none',
                mode='lines',
                name=f"{rel_type.replace('_', ' ').title()}",
                showlegend=True,
                legendgroup="edges"
            ))
        
        return traces

    def create_enhanced_node_traces(self, graph: nx.Graph, pos: dict, audience_filter: str = None) -> List[go.Scatter]:
        """Create enhanced node traces with better grouping"""
        node_groups = defaultdict(lambda: {
            'x': [], 'y': [], 'text': [], 'hovertext': [], 'sizes': [], 'colors': []
        })
        
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]
            
            # Group by audience and type
            primary_audience = node_data['primary_audience']
            node_type = node_data['type']
            importance = node_data['importance']
            
            group_key = f"{primary_audience}_{node_type}"
            
            x, y = pos[node_id]
            node_groups[group_key]['x'].append(x)
            node_groups[group_key]['y'].append(y)
            
            # Node display
            source_abbrev = node_data['source'].replace('_api', '').replace('_', ' ').title()[:8]
            node_groups[group_key]['text'].append(source_abbrev)
            
            # Enhanced hover info
            content_preview = textwrap.shorten(node_data['content'], width=80)
            relevance_info = []
            for aud, score in node_data['audience_relevance'].items():
                if score > 0.1:
                    relevance_info.append(f"{aud}: {score:.2f}")
            
            hover_text = (
                f"<b>{node_type.title()}: {source_abbrev}</b><br>"
                f"<i>{content_preview}</i><br><br>"
                f"🎯 Primary Audience: {primary_audience.title()}<br>"
                f"⭐ Importance: {importance.title()}<br>"
                f"🔢 Confidence: {node_data['confidence']}<br>"
                f"📊 Relevance: {', '.join(relevance_info) if relevance_info else 'General'}<br>"
                f"🏷️ Tags: {', '.join(node_data['tags'][:4])}"
            )
            node_groups[group_key]['hovertext'].append(hover_text)
            
            # Node size and color
            size_map = {'high': 30, 'medium': 22, 'low': 16}
            node_groups[group_key]['sizes'].append(size_map[importance])
            
            # Color based on audience
            base_color = self.audiences.get(primary_audience, {}).get('color', '#95A5A6')
            node_groups[group_key]['colors'].append(base_color)
        
        # Create traces
        traces = []
        for group_key, group_data in node_groups.items():
            if not group_data['x']:  # Skip empty groups
                continue
                
            audience, node_type = group_key.split('_', 1)
            display_name = f"{audience.title()} {node_type.title()}s"
            
            traces.append(go.Scatter(
                x=group_data['x'], 
                y=group_data['y'],
                mode='markers+text',
                marker=dict(
                    size=group_data['sizes'],
                    color=group_data['colors'],
                    opacity=0.8,
                    line=dict(width=2, color='white'),
                    symbol=('circle' if node_type == 'metric' else 'diamond')
                ),
                text=group_data['text'],
                textposition="middle center",
                textfont=dict(size=10, color='white'),
                hovertext=group_data['hovertext'],
                hoverinfo='text',
                name=display_name,
                showlegend=True,
                legendgroup="nodes"
            ))
        
        return traces

    def create_insight_priority_dashboard(self):
        """Create dashboard showing prioritized insights by audience"""
        # Prepare data for dashboard
        cluster_data = []
        for cluster in self.clusters:
            cluster_data.append({
                'Audience': cluster.audience.title(),
                'Cluster': cluster.name,
                'Priority': cluster.priority,
                'Insights Count': len(cluster.nodes),
                'Key Metrics': len(cluster.key_metrics),
                'Description': cluster.description
            })
        
        if not cluster_data:
            return go.Figure().add_annotation(
                text="No insight clusters found. Generate graph with more diverse data.",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16)
            )
        
        df = pd.DataFrame(cluster_data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Insights by Priority', 
                'Insights by Audience',
                'Cluster Sizes', 
                'Priority Distribution'
            ),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Priority distribution
        priority_counts = df['Priority'].value_counts()
        fig.add_trace(
            go.Bar(x=priority_counts.index, y=priority_counts.values, 
                   name="Priority", marker_color='#FF6B6B'),
            row=1, col=1
        )
        
        # Audience distribution  
        audience_counts = df['Audience'].value_counts()
        fig.add_trace(
            go.Pie(labels=audience_counts.index, values=audience_counts.values,
                   name="Audience"),
            row=1, col=2
        )
        
        # Cluster sizes
        fig.add_trace(
            go.Scatter(x=df['Insights Count'], y=df['Key Metrics'],
                       mode='markers+text', text=df['Cluster'],
                       textposition="top center",
                       marker=dict(size=10, color='#4ECDC4'),
                       name="Clusters"),
            row=2, col=1
        )
        
        # Priority by audience
        priority_audience = df.groupby(['Audience', 'Priority']).size().unstack(fill_value=0)
        for priority in ['high', 'medium', 'low']:
            if priority in priority_audience.columns:
                fig.add_trace(
                    go.Bar(x=priority_audience.index, y=priority_audience[priority],
                           name=f"{priority.title()} Priority"),
                    row=2, col=2
                )
        
        fig.update_layout(
            title_text="Insight Clusters Dashboard",
            showlegend=True,
            height=800
        )
        
        return fig, df

    def generate_audience_report(self, audience: str) -> dict:
        """Generate detailed report for specific audience"""
        audience_clusters = [c for c in self.clusters if c.audience == audience]
        
        if not audience_clusters:
            return {
                'audience': audience,
                'summary': f"No specific insights found for {audience}",
                'recommendations': ["Generate more data relevant to this audience"],
                'priority_insights': [],
                'key_metrics': []
            }
        
        # Combine insights
        all_insights = []
        all_metrics = []
        high_priority_insights = []
        
        for cluster in audience_clusters:
            all_insights.extend(cluster.actionable_insights)
            all_metrics.extend(cluster.key_metrics)
            if cluster.priority == 'high':
                high_priority_insights.extend(cluster.actionable_insights)
        
        return {
            'audience': audience,
            'cluster_count': len(audience_clusters),
            'high_priority_clusters': len([c for c in audience_clusters if c.priority == 'high']),
            'summary': f"Found {len(audience_clusters)} insight clusters for {audience}",
            'priority_insights': list(set(high_priority_insights))[:5],
            'key_metrics': list(set(all_metrics))[:5],
            'actionable_insights': list(set(all_insights))[:8],
            'clusters': [
                {
                    'name': c.name,
                    'priority': c.priority,
                    'description': c.description,
                    'insights': c.actionable_insights
                } for c in audience_clusters
            ]
        }

    def save_enhanced_visualizations(self, output_dir: str = "visualizations/enhanced"):
        """Save all enhanced visualizations"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate visualizations for each audience
        for audience in self.audiences.keys():
            fig = self.create_audience_filtered_view(audience)
            fig.write_html(f"{output_dir}/{audience}_focused_graph.html")
        
        # Generate complete graph
        complete_fig = self.create_audience_filtered_view()
        complete_fig.write_html(f"{output_dir}/complete_enhanced_graph.html")
        
        # Generate dashboard
        dashboard_fig, cluster_df = self.create_insight_priority_dashboard()
        dashboard_fig.write_html(f"{output_dir}/insights_dashboard.html")
        cluster_df.to_csv(f"{output_dir}/insight_clusters.csv", index=False)
        
        # Generate audience reports
        reports = {}
        for audience in self.audiences.keys():
            reports[audience] = self.generate_audience_report(audience)
        
        with open(f"{output_dir}/audience_reports.json", 'w') as f:
            json.dump(reports, f, indent=2)
        
        print(f"✅ Enhanced visualizations saved to {output_dir}")
        return output_dir

def main():
    """Main function to run enhanced visualizer"""
    print("🚀 Starting Enhanced Graph Visualization...")
    
    visualizer = EnhancedGraphVisualizer(
        "graphs/nodes/flowmetrics_nodes.json",
        "graphs/edges/flowmetrics_edges.json"
    )
    
    print(f"📊 Loaded {len(visualizer.graph.nodes())} nodes and {len(visualizer.graph.edges())} edges")
    print(f"🎯 Generated {len(visualizer.clusters)} insight clusters")
    
    # Create output directory
    import os
    output_dir = "graphs/visualizations/enhanced"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate visualizations
    print("\n📈 Generating audience-specific views...")
    
    for audience in visualizer.audiences.keys():
        print(f"  Creating {audience} view...")
        fig = visualizer.create_audience_filtered_view(audience)
        fig.write_html(f"{output_dir}/{audience}_focused_graph.html")
    
    # Generate complete view
    print("  Creating complete view...")
    complete_fig = visualizer.create_audience_filtered_view()
    complete_fig.write_html(f"{output_dir}/complete_enhanced_graph.html")
    
    # Save cluster analysis
    print("💾 Saving cluster analysis...")
    cluster_reports = {}
    for audience in visualizer.audiences.keys():
        audience_clusters = [c for c in visualizer.clusters if c.audience == audience]
        cluster_reports[audience] = {
            'cluster_count': len(audience_clusters),
            'clusters': [
                {
                    'name': c.name,
                    'priority': c.priority,
                    'description': c.description,
                    'node_count': len(c.nodes),
                    'key_metrics': c.key_metrics,
                    'actionable_insights': c.actionable_insights
                } for c in audience_clusters
            ]
        }
    
    with open(f"{output_dir}/insight_clusters.json", 'w') as f:
        json.dump(cluster_reports, f, indent=2)
    
    print(f"\n✅ Enhanced visualizations complete!")
    print(f"📁 Files saved to: {output_dir}")
    print(f"🔍 Open the HTML files in your browser to explore the enhanced graphs")
    
    # Print summary
    print(f"\n📋 Summary:")
    for audience, report in cluster_reports.items():
        if report['cluster_count'] > 0:
            print(f"  {audience.title()}: {report['cluster_count']} insight clusters")
            for cluster in report['clusters'][:1]:  # Show first cluster
                print(f"    • {cluster['name']} ({cluster['priority']} priority)")

if __name__ == "__main__":
    main() 