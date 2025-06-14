#!/usr/bin/env python3
"""
Interactive Dashboard for Enhanced Graph Exploration
Provides intuitive filtering and navigation of the semantic graph
"""

import streamlit as st
import pandas as pd
import json
from enhanced_visualizer import EnhancedGraphVisualizer
import plotly.graph_objects as go
from collections import defaultdict
import numpy as np

st.set_page_config(
    page_title="FlowMetrics Knowledge Graph Explorer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_visualizer():
    """Load the enhanced visualizer (cached for performance)"""
    return EnhancedGraphVisualizer(
        "graphs/nodes/flowmetrics_nodes.json",
        "graphs/edges/flowmetrics_edges.json"
    )

def main():
    st.title("🧠 FlowMetrics Knowledge Graph Explorer")
    st.markdown("**Navigate your data insights with intelligent filtering and audience-specific views**")
    
    # Load visualizer
    visualizer = load_visualizer()
    
    # Sidebar controls
    st.sidebar.header("🎛️ Graph Controls")
    
    # Audience filter
    audience_options = ["All Audiences"] + list(visualizer.audiences.keys())
    selected_audience = st.sidebar.selectbox(
        "👥 Focus on Audience:",
        audience_options,
        help="Filter graph to show insights most relevant to specific audience"
    )
    
    # Importance filter
    importance_levels = st.sidebar.multiselect(
        "⭐ Importance Levels:",
        ["high", "medium", "low"],
        default=["high", "medium"],
        help="Show nodes with selected importance levels"
    )
    
    # Node type filter
    node_types = st.sidebar.multiselect(
        "📊 Data Types:",
        ["metric", "insight"],
        default=["metric", "insight"],
        help="Include metrics, insights, or both"
    )
    
    # Minimum relevance threshold
    min_relevance = st.sidebar.slider(
        "🎯 Minimum Relevance Score:",
        0.0, 1.0, 0.1, 0.05,
        help="Minimum audience relevance score to include nodes"
    )
    
    # Edge strength filter
    edge_strength = st.sidebar.multiselect(
        "🔗 Connection Strength:",
        ["strong", "medium", "weak"],
        default=["strong", "medium"],
        help="Show connections with selected strength levels"
    )
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Graph View", "🎯 Insights Dashboard", "📋 Audience Reports", "🔍 Data Explorer"])
    
    with tab1:
        st.header("Interactive Knowledge Graph")
        
        # Apply filters and generate graph
        filtered_graph = apply_filters(
            visualizer, selected_audience, importance_levels, 
            node_types, min_relevance, edge_strength
        )
        
        if len(filtered_graph.nodes()) == 0:
            st.warning("🚫 No data matches your current filters. Try adjusting the criteria.")
        else:
            # Display graph stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nodes", len(filtered_graph.nodes()))
            with col2:
                st.metric("Connections", len(filtered_graph.edges()))
            with col3:
                audiences_represented = set(
                    filtered_graph.nodes[n]['primary_audience'] 
                    for n in filtered_graph.nodes()
                )
                st.metric("Audiences", len(audiences_represented))
            with col4:
                high_importance = sum(
                    1 for n in filtered_graph.nodes() 
                    if filtered_graph.nodes[n]['importance'] == 'high'
                )
                st.metric("High Priority", high_importance)
            
            # Generate and display graph
            title = f"Knowledge Graph - {selected_audience}" if selected_audience != "All Audiences" else "Complete Knowledge Graph"
            fig = visualizer.create_interactive_network(
                filtered_graph, title, 
                selected_audience if selected_audience != "All Audiences" else None
            )
            
            st.plotly_chart(fig, use_container_width=True, height=700)
            
            # Show filtered node details
            if st.checkbox("📋 Show Node Details"):
                show_node_details(filtered_graph)
    
    with tab2:
        st.header("📊 Insights Dashboard")
        
        # Cluster analysis
        st.subheader("🎯 Insight Clusters by Audience")
        
        cluster_data = []
        for cluster in visualizer.clusters:
            cluster_data.append({
                'Audience': cluster.audience.title(),
                'Cluster Name': cluster.name,
                'Priority': cluster.priority,
                'Nodes': len(cluster.nodes),
                'Description': cluster.description
            })
        
        if cluster_data:
            cluster_df = pd.DataFrame(cluster_data)
            
            # Priority distribution chart
            col1, col2 = st.columns(2)
            
            with col1:
                priority_counts = cluster_df['Priority'].value_counts()
                fig_priority = go.Figure(data=[
                    go.Bar(x=priority_counts.index, y=priority_counts.values,
                           marker_color=['#E74C3C', '#F39C12', '#27AE60'])
                ])
                fig_priority.update_layout(
                    title="Clusters by Priority Level",
                    xaxis_title="Priority",
                    yaxis_title="Number of Clusters"
                )
                st.plotly_chart(fig_priority, use_container_width=True)
            
            with col2:
                audience_counts = cluster_df['Audience'].value_counts()
                fig_audience = go.Figure(data=[
                    go.Pie(labels=audience_counts.index, values=audience_counts.values,
                           hole=0.3)
                ])
                fig_audience.update_layout(title="Clusters by Audience")
                st.plotly_chart(fig_audience, use_container_width=True)
            
            # Cluster details table
            st.subheader("📋 Cluster Details")
            
            # Filter clusters
            selected_priority = st.selectbox(
                "Filter by Priority:",
                ["All"] + list(cluster_df['Priority'].unique()),
                key="cluster_priority"
            )
            
            filtered_clusters = cluster_df
            if selected_priority != "All":
                filtered_clusters = cluster_df[cluster_df['Priority'] == selected_priority]
            
            st.dataframe(
                filtered_clusters,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("🔍 No insight clusters found with current data. Consider adding more diverse data sources.")
    
    with tab3:
        st.header("📋 Audience-Specific Reports")
        
        # Generate reports for each audience
        for audience in visualizer.audiences.keys():
            with st.expander(f"📊 {audience.title()} Report"):
                report = generate_audience_report(visualizer, audience)
                
                if report['cluster_count'] > 0:
                    st.success(f"Found {report['cluster_count']} insight clusters")
                    
                    # Priority insights
                    if report['priority_insights']:
                        st.subheader("🎯 Priority Insights")
                        for insight in report['priority_insights']:
                            st.markdown(f"• {insight}")
                    
                    # Key metrics
                    if report['key_metrics']:
                        st.subheader("📈 Key Metrics")
                        for metric in report['key_metrics']:
                            st.markdown(f"• {metric}")
                    
                    # Actionable insights
                    if report['actionable_insights']:
                        st.subheader("💡 Actionable Insights")
                        for insight in report['actionable_insights']:
                            st.markdown(f"• {insight}")
                else:
                    st.info(f"No specific clusters found for {audience}. Consider enriching data with {audience}-relevant content.")
    
    with tab4:
        st.header("🔍 Raw Data Explorer")
        
        # Node data explorer
        st.subheader("📊 Node Data")
        
        node_data = []
        for node_id in visualizer.graph.nodes():
            node = visualizer.graph.nodes[node_id]
            node_data.append({
                'ID': node_id[:8],
                'Type': node['type'],
                'Content': node['content'][:100] + '...' if len(node['content']) > 100 else node['content'],
                'Source': node['source'],
                'Primary Audience': node['primary_audience'],
                'Importance': node['importance'],
                'Confidence': node['confidence'],
                'Tags': ', '.join(node['tags'][:3])
            })
        
        node_df = pd.DataFrame(node_data)
        
        # Filters for node data
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_audience = st.selectbox(
                "Filter by Audience:",
                ["All"] + list(node_df['Primary Audience'].unique()),
                key="node_audience"
            )
        with col2:
            filter_type = st.selectbox(
                "Filter by Type:",
                ["All"] + list(node_df['Type'].unique()),
                key="node_type"
            )
        with col3:
            filter_importance = st.selectbox(
                "Filter by Importance:",
                ["All"] + list(node_df['Importance'].unique()),
                key="node_importance"
            )
        
        # Apply filters
        filtered_node_df = node_df
        if filter_audience != "All":
            filtered_node_df = filtered_node_df[filtered_node_df['Primary Audience'] == filter_audience]
        if filter_type != "All":
            filtered_node_df = filtered_node_df[filtered_node_df['Type'] == filter_type]
        if filter_importance != "All":
            filtered_node_df = filtered_node_df[filtered_node_df['Importance'] == filter_importance]
        
        st.dataframe(filtered_node_df, use_container_width=True, hide_index=True)
        
        # Edge data explorer
        st.subheader("🔗 Connection Data")
        
        edge_data = []
        for edge in visualizer.graph.edges(data=True):
            source_content = visualizer.graph.nodes[edge[0]]['content'][:50]
            target_content = visualizer.graph.nodes[edge[1]]['content'][:50]
            
            edge_data.append({
                'Source': source_content + '...',
                'Target': target_content + '...',
                'Relationship': edge[2]['relationship_type'],
                'Weight': round(edge[2]['weight'], 3),
                'Similarity': round(edge[2]['similarity'], 3),
                'Strength': edge[2]['strength']
            })
        
        edge_df = pd.DataFrame(edge_data)
        st.dataframe(edge_df, use_container_width=True, hide_index=True)

def apply_filters(visualizer, audience, importance_levels, node_types, min_relevance, edge_strength):
    """Apply user-selected filters to the graph"""
    # Start with all nodes
    filtered_nodes = []
    
    for node_id in visualizer.graph.nodes():
        node_data = visualizer.graph.nodes[node_id]
        
        # Check importance level
        if node_data['importance'] not in importance_levels:
            continue
        
        # Check node type
        if node_data['type'] not in node_types:
            continue
        
        # Check audience relevance
        if audience != "All Audiences":
            relevance = node_data['audience_relevance'].get(audience, 0)
            primary_audience = node_data['primary_audience']
            
            if relevance < min_relevance and primary_audience != audience:
                continue
        
        filtered_nodes.append(node_id)
    
    # Create subgraph with filtered nodes
    subgraph = visualizer.graph.subgraph(filtered_nodes)
    
    # Filter edges by strength
    edges_to_remove = []
    for edge in subgraph.edges(data=True):
        if edge[2]['strength'] not in edge_strength:
            edges_to_remove.append((edge[0], edge[1]))
    
    # Create final filtered graph
    final_graph = subgraph.copy()
    final_graph.remove_edges_from(edges_to_remove)
    
    return final_graph

def show_node_details(graph):
    """Show detailed information about nodes"""
    node_details = []
    
    for node_id in graph.nodes():
        node = graph.nodes[node_id]
        
        # Calculate connections
        connections = len(list(graph.neighbors(node_id)))
        
        # Format relevance scores
        relevance_scores = []
        for aud, score in node['audience_relevance'].items():
            if score > 0.1:
                relevance_scores.append(f"{aud}: {score:.2f}")
        
        node_details.append({
            'Content': node['content'][:80] + '...' if len(node['content']) > 80 else node['content'],
            'Source': node['source'],
            'Type': node['type'].title(),
            'Audience': node['primary_audience'].title(),
            'Importance': node['importance'].title(),
            'Confidence': f"{node['confidence']:.2f}",
            'Connections': connections,
            'Relevance': '; '.join(relevance_scores) if relevance_scores else 'General',
            'Tags': ', '.join(node['tags'][:4])
        })
    
    details_df = pd.DataFrame(node_details)
    st.dataframe(details_df, use_container_width=True, hide_index=True)

def generate_audience_report(visualizer, audience):
    """Generate a detailed report for a specific audience"""
    audience_clusters = [c for c in visualizer.clusters if c.audience == audience]
    
    if not audience_clusters:
        return {
            'cluster_count': 0,
            'priority_insights': [],
            'key_metrics': [],
            'actionable_insights': []
        }
    
    # Combine all insights
    all_priority_insights = []
    all_key_metrics = []
    all_actionable_insights = []
    
    for cluster in audience_clusters:
        if cluster.priority == 'high':
            all_priority_insights.extend(cluster.actionable_insights)
        all_key_metrics.extend(cluster.key_metrics)
        all_actionable_insights.extend(cluster.actionable_insights)
    
    return {
        'cluster_count': len(audience_clusters),
        'priority_insights': list(set(all_priority_insights))[:5],
        'key_metrics': list(set(all_key_metrics))[:5],
        'actionable_insights': list(set(all_actionable_insights))[:8]
    }

if __name__ == "__main__":
    main() 