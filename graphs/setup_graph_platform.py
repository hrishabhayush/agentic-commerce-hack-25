#!/usr/bin/env python3
"""
Setup Script for Agentic Commerce Graph Visualization Platform
Initializes Neo4j database and starts the web server
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("🔍 Checking dependencies...")
    
    try:
        import neo4j
        import fastapi
        import uvicorn
        logger.info("✅ Python dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.info("Install with: pip install -r requirements.txt")
        return False

def check_neo4j():
    """Check if Neo4j is running"""
    logger.info("🔍 Checking Neo4j connection...")
    
    try:
        from neo4j_client import Neo4jGraphClient
        client = Neo4jGraphClient()
        client.verify_connectivity()
        client.close()
        logger.info("✅ Neo4j is running and accessible")
        return True
    except Exception as e:
        logger.error(f"❌ Neo4j connection failed: {e}")
        logger.info("Please ensure Neo4j is running on bolt://localhost:7687")
        logger.info("Default credentials: username=neo4j, password=password")
        return False

def initialize_database():
    """Initialize Neo4j database with graph data"""
    logger.info("📊 Initializing graph database...")
    
    try:
        from neo4j_client import initialize_neo4j_graph
        
        nodes_file = "nodes/flowmetrics_nodes.json"
        edges_file = "edges/flowmetrics_edges.json"
        
        if not os.path.exists(nodes_file) or not os.path.exists(edges_file):
            logger.error(f"❌ Graph data files not found: {nodes_file}, {edges_file}")
            return False
        
        client = initialize_neo4j_graph(nodes_file, edges_file)
        overview = client.get_graph_overview()
        
        logger.info(f"✅ Database initialized with {overview['total_nodes']} nodes and {overview['total_relationships']} relationships")
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def create_missing_js_files():
    """Create missing JavaScript files if they don't exist"""
    logger.info("📝 Creating JavaScript files...")
    
    js_file = "static/js/graph_visualization.js"
    if not os.path.exists(js_file):
        logger.info(f"Creating {js_file}...")
        
        js_content = '''/**
 * Professional Graph Visualization Platform
 * Main JavaScript file for Linkurious-like functionality
 */

class GraphVisualization {
    constructor() {
        this.network = null;
        this.nodes = new vis.DataSet([]);
        this.edges = new vis.DataSet([]);
        this.currentData = { nodes: [], edges: [] };
        this.selectedNode = null;
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        this.showLoading(true);
        
        try {
            await this.loadInitialData();
            this.setupGraph();
            this.loadFilters();
            this.updateStats();
            this.showLoading(false);
        } catch (error) {
            console.error('Failed to initialize graph:', error);
            this.showError('Failed to load graph data');
        }
    }
    
    setupEventListeners() {
        // Search
        document.getElementById('search-btn')?.addEventListener('click', () => this.performSearch());
        document.getElementById('search-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });
        
        // Filters
        document.getElementById('apply-filters-btn')?.addEventListener('click', () => this.applyFilters());
        document.getElementById('clear-filters-btn')?.addEventListener('click', () => this.clearFilters());
        
        // Graph controls
        document.getElementById('zoom-in-btn')?.addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out-btn')?.addEventListener('click', () => this.zoomOut());
        document.getElementById('fit-btn')?.addEventListener('click', () => this.fitToScreen());
    }
    
    async loadInitialData() {
        const response = await fetch('/api/graph/filtered', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ min_confidence: 0.0, min_weight: 0.3, limit: 50 })
        });
        
        const data = await response.json();
        this.currentData = data;
        this.updateGraphData(data);
    }
    
    async loadFilters() {
        try {
            const nodeTypesResponse = await fetch('/api/node-types');
            const nodeTypesData = await nodeTypesResponse.json();
            this.populateCheckboxGroup('node-types-filter', nodeTypesData.node_types || []);
            
            const sourcesResponse = await fetch('/api/sources');
            const sourcesData = await sourcesResponse.json();
            this.populateCheckboxGroup('sources-filter', sourcesData.sources || []);
        } catch (error) {
            console.error('Error loading filters:', error);
        }
    }
    
    populateCheckboxGroup(containerId, items) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        items.forEach(item => {
            if (item) {
                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = item;
                checkbox.checked = true;
                
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(item));
                container.appendChild(label);
            }
        });
    }
    
    setupGraph() {
        const container = document.getElementById('graph-container');
        if (!container) return;
        
        const options = {
            nodes: {
                shape: 'dot',
                size: 20,
                font: { size: 12, color: '#2c3e50' },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                smooth: { type: 'continuous', roundness: 0.2 },
                arrows: { to: { enabled: true, scaleFactor: 0.5 } }
            },
            physics: {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -2000,
                    centralGravity: 0.3,
                    springLength: 95
                }
            },
            interaction: { hover: true }
        };
        
        this.network = new vis.Network(container, { nodes: this.nodes, edges: this.edges }, options);
        
        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                this.selectNode(params.nodes[0]);
            }
        });
    }
    
    updateGraphData(data) {
        const processedNodes = (data.nodes || []).map(node => ({
            id: node.id,
            label: this.truncateText(node.content, 30),
            title: `${node.type}: ${node.content}\\nSource: ${node.source}`,
            color: node.type === 'metric' ? '#3498db' : '#e74c3c',
            size: Math.max(15, (node.confidence || 0.5) * 30)
        }));
        
        const processedEdges = (data.edges || []).map(edge => ({
            id: `${edge.source_id}-${edge.target_id}`,
            from: edge.source_id,
            to: edge.target_id,
            width: Math.max(1, (edge.weight || 0.5) * 5),
            title: `Weight: ${(edge.weight || 0).toFixed(3)}`
        }));
        
        this.nodes.clear();
        this.edges.clear();
        this.nodes.add(processedNodes);
        this.edges.add(processedEdges);
        
        this.updateStats();
    }
    
    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    async selectNode(nodeId) {
        const node = this.nodes.get(nodeId);
        if (node) {
            this.displayNodeDetails(node);
        }
    }
    
    displayNodeDetails(node) {
        const container = document.getElementById('node-details');
        if (!container) return;
        
        container.innerHTML = `
            <div><strong>Type:</strong> ${node.label}</div>
            <div><strong>ID:</strong> ${node.id}</div>
            <div><strong>Title:</strong> ${node.title || 'N/A'}</div>
        `;
    }
    
    async performSearch() {
        const query = document.getElementById('search-input')?.value?.trim();
        if (!query) return;
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, limit: 20 })
            });
            
            const results = await response.json();
            this.displaySearchResults(results.results || []);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }
    
    displaySearchResults(results) {
        const container = document.getElementById('search-results');
        if (!container) return;
        
        if (results.length === 0) {
            container.innerHTML = '<p>No results found</p>';
            return;
        }
        
        const html = results.map(node => `
            <div class="search-result-item" onclick="graphViz.focusOnNode('${node.id}')">
                <div class="content">${this.truncateText(node.content, 50)}</div>
                <div class="meta">${node.type} • ${node.source}</div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    focusOnNode(nodeId) {
        if (this.network) {
            this.network.focus(nodeId, { scale: 1.5, animation: true });
            this.selectNode(nodeId);
        }
    }
    
    async applyFilters() {
        const filters = this.getFilterValues();
        
        try {
            const response = await fetch('/api/graph/filtered', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(filters)
            });
            
            const data = await response.json();
            this.currentData = data;
            this.updateGraphData(data);
        } catch (error) {
            console.error('Filter failed:', error);
        }
    }
    
    getFilterValues() {
        const nodeTypes = Array.from(document.querySelectorAll('#node-types-filter input:checked') || [])
            .map(cb => cb.value);
        
        const sources = Array.from(document.querySelectorAll('#sources-filter input:checked') || [])
            .map(cb => cb.value);
        
        return {
            node_types: nodeTypes.length > 0 ? nodeTypes : null,
            sources: sources.length > 0 ? sources : null,
            min_confidence: parseFloat(document.getElementById('confidence-slider')?.value || 0),
            min_weight: parseFloat(document.getElementById('weight-slider')?.value || 0.3),
            limit: 100
        };
    }
    
    clearFilters() {
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
        const confSlider = document.getElementById('confidence-slider');
        const weightSlider = document.getElementById('weight-slider');
        
        if (confSlider) confSlider.value = 0;
        if (weightSlider) weightSlider.value = 0.3;
        
        this.applyFilters();
    }
    
    zoomIn() {
        if (this.network) {
            const scale = this.network.getScale() * 1.2;
            this.network.moveTo({ scale });
        }
    }
    
    zoomOut() {
        if (this.network) {
            const scale = this.network.getScale() * 0.8;
            this.network.moveTo({ scale });
        }
    }
    
    fitToScreen() {
        if (this.network) {
            this.network.fit({ animation: true });
        }
    }
    
    updateStats() {
        const setContent = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value || 0;
        };
        
        setContent('total-nodes', this.currentData.total_nodes);
        setContent('total-edges', this.currentData.total_edges);
        setContent('visible-nodes', this.nodes.length);
        setContent('visible-edges', this.edges.length);
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }
    
    showError(message) {
        const info = document.getElementById('graph-info');
        if (info) info.textContent = `Error: ${message}`;
        this.showLoading(false);
    }
    
    logActivity(message) {
        const log = document.getElementById('activity-log');
        if (!log) return;
        
        const time = new Date().toLocaleTimeString();
        const activityHtml = `
            <div class="activity-item">
                <span class="activity-text">${message}</span>
                <span class="activity-time">${time}</span>
            </div>
        `;
        
        log.insertAdjacentHTML('afterbegin', activityHtml);
        
        const items = log.querySelectorAll('.activity-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }
}

// Initialize
let graphViz;
document.addEventListener('DOMContentLoaded', () => {
    graphViz = new GraphVisualization();
    window.graphViz = graphViz;
});'''
        
        os.makedirs(os.path.dirname(js_file), exist_ok=True)
        with open(js_file, 'w') as f:
            f.write(js_content)
        
        logger.info(f"✅ Created {js_file}")

def start_server():
    """Start the FastAPI development server"""
    logger.info("🚀 Starting Graph Visualization Server...")
    
    try:
        # Import and start the server
        from graph_api import start_server
        start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        return False
    
    return True

def print_startup_info():
    """Print startup information and instructions"""
    print("\n" + "="*60)
    print("🎯 AGENTIC COMMERCE GRAPH VISUALIZATION PLATFORM")
    print("="*60)
    print(f"📊 Dashboard: http://localhost:8000")
    print(f"🔍 API Docs:  http://localhost:8000/docs")
    print(f"🌐 Health:    http://localhost:8000/api/health")
    print("\n🎮 FEATURES:")
    print("  • Interactive graph visualization")
    print("  • Advanced search and filtering")
    print("  • Multiple layout algorithms")
    print("  • Real-time collaboration")
    print("  • Data export capabilities")
    print("  • Audience-specific views")
    print("\n💡 USAGE:")
    print("  • Use the search bar to find specific nodes")
    print("  • Apply filters to focus on relevant data")
    print("  • Click nodes to see detailed information")
    print("  • Use toolbar controls for graph navigation")
    print("  • Export data in various formats")
    print("="*60)

def main():
    """Main setup function"""
    print("🎯 Setting up Agentic Commerce Graph Visualization Platform...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Neo4j
    if not check_neo4j():
        print("\n📋 Neo4j Setup Instructions:")
        print("1. Install Neo4j Desktop or Community Edition")
        print("2. Create a new database with:")
        print("   - Username: neo4j")
        print("   - Password: password")
        print("   - Port: 7687")
        print("3. Start the database")
        print("4. Run this setup script again")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Create missing files
    create_missing_js_files()
    
    # Print info
    print_startup_info()
    
    # Start server
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main() 