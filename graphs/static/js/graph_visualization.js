/**
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
        this.analytics = null;
        
        // Initialize the application
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
            this.showError('Failed to load graph data. Please check your connection.');
        }
    }
    
    setupEventListeners() {
        // Search functionality
        document.getElementById('search-btn').addEventListener('click', () => this.performSearch());
        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });
        
        // Filter controls
        document.getElementById('apply-filters-btn').addEventListener('click', () => this.applyFilters());
        document.getElementById('clear-filters-btn').addEventListener('click', () => this.clearFilters());
        
        // Range sliders
        document.getElementById('confidence-slider').addEventListener('input', (e) => {
            document.getElementById('confidence-value').textContent = e.target.value;
        });
        
        document.getElementById('weight-slider').addEventListener('input', (e) => {
            document.getElementById('weight-value').textContent = e.target.value;
        });
        
        // Layout controls
        document.getElementById('apply-layout-btn').addEventListener('click', () => this.applyLayout());
        
        // Graph toolbar
        document.getElementById('zoom-in-btn').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out-btn').addEventListener('click', () => this.zoomOut());
        document.getElementById('fit-btn').addEventListener('click', () => this.fitToScreen());
        document.getElementById('center-btn').addEventListener('click', () => this.centerGraph());
        
        // Export functionality
        document.getElementById('export-btn').addEventListener('click', () => this.showExportModal());
        document.getElementById('download-btn').addEventListener('click', () => this.downloadData());
        
        // Modal controls
        document.querySelector('.close').addEventListener('click', () => this.hideExportModal());
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideExportModal();
            }
        });
        
        // Audience filter
        document.getElementById('audience-select').addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadAudienceGraph(e.target.value);
            }
        });
    }
    
    async loadInitialData() {
        try {
            // Load graph overview
            const overviewResponse = await fetch('/api/overview');
            const overview = await overviewResponse.json();
            
            // Load initial filtered graph
            const graphResponse = await fetch('/api/graph/filtered', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    min_confidence: 0.0,
                    min_weight: 0.3,
                    limit: 100
                })
            });
            
            const graphData = await graphResponse.json();
            this.currentData = graphData;
            
            this.updateGraphData(graphData);
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            throw error;
        }
    }
    
    async loadFilters() {
        try {
            // Load available node types
            const nodeTypesResponse = await fetch('/api/node-types');
            const nodeTypesData = await nodeTypesResponse.json();
            this.populateCheckboxGroup('node-types-filter', nodeTypesData.node_types);
            
            // Load available sources
            const sourcesResponse = await fetch('/api/sources');
            const sourcesData = await sourcesResponse.json();
            this.populateCheckboxGroup('sources-filter', sourcesData.sources);
            
        } catch (error) {
            console.error('Error loading filters:', error);
        }
    }
    
    populateCheckboxGroup(containerId, items) {
        const container = document.getElementById(containerId);
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
        
        const options = {
            nodes: {
                shape: 'dot',
                size: 20,
                font: {
                    size: 12,
                    color: '#2c3e50'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                color: { inherit: 'from' },
                smooth: {
                    type: 'continuous',
                    roundness: 0.2
                },
                arrows: {
                    to: { enabled: true, scaleFactor: 0.5 }
                }
            },
            physics: {
                enabled: true,
                stabilization: { iterations: 100 },
                barnesHut: {
                    gravitationalConstant: -2000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                selectConnectedEdges: false,
                tooltipDelay: 200
            },
            layout: {
                improvedLayout: true
            }
        };
        
        this.network = new vis.Network(container, { nodes: this.nodes, edges: this.edges }, options);
        
        // Setup event handlers
        this.network.on('click', (params) => this.onNodeClick(params));
        this.network.on('hoverNode', (params) => this.onNodeHover(params));
        this.network.on('blurNode', () => this.onNodeBlur());
        this.network.on('stabilizationIterationsDone', () => {
            this.updateGraphInfo('Graph stabilized');
        });
    }
    
    updateGraphData(data) {
        // Process nodes
        const processedNodes = data.nodes.map(node => ({
            id: node.id,
            label: this.truncateText(node.content, 30),
            title: this.createNodeTooltip(node),
            color: this.getNodeColor(node.type),
            size: this.getNodeSize(node.confidence),
            type: node.type,
            ...node
        }));
        
        // Process edges
        const processedEdges = data.edges.map(edge => ({
            id: `${edge.source_id}-${edge.target_id}`,
            from: edge.source_id,
            to: edge.target_id,
            width: Math.max(1, edge.weight * 5),
            color: this.getEdgeColor(edge.relationship_type),
            title: `Weight: ${edge.weight.toFixed(3)}\nType: ${edge.relationship_type}`,
            ...edge
        }));
        
        // Update datasets
        this.nodes.clear();
        this.edges.clear();
        this.nodes.add(processedNodes);
        this.edges.add(processedEdges);
        
        this.updateStats();
    }
    
    getNodeColor(type) {
        const colors = {
            'metric': '#3498db',
            'insight': '#e74c3c',
            'default': '#95a5a6'
        };
        return colors[type] || colors.default;
    }
    
    getNodeSize(confidence) {
        return Math.max(15, confidence * 30);
    }
    
    getEdgeColor(type) {
        const colors = {
            'relevance': '#7f8c8d',
            'correlation': '#2ecc71',
            'default': '#bdc3c7'
        };
        return colors[type] || colors.default;
    }
    
    createNodeTooltip(node) {
        return `
            <strong>${node.type}</strong><br/>
            ${node.content}<br/>
            <em>Source: ${node.source}</em><br/>
            <em>Confidence: ${(node.confidence * 100).toFixed(1)}%</em>
        `;
    }
    
    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    onNodeClick(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            this.selectNode(nodeId);
        }
    }
    
    onNodeHover(params) {
        // Highlight connected nodes
        const connectedNodes = this.network.getConnectedNodes(params.node);
        const connectedEdges = this.network.getConnectedEdges(params.node);
        
        const updateNodes = [{
            id: params.node,
            borderWidth: 4,
            borderColor: '#3498db'
        }];
        
        connectedNodes.forEach(nodeId => {
            updateNodes.push({
                id: nodeId,
                borderWidth: 3,
                borderColor: '#e74c3c'
            });
        });
        
        this.nodes.update(updateNodes);
    }
    
    onNodeBlur() {
        // Reset node highlighting
        const updates = this.nodes.map(node => ({
            id: node.id,
            borderWidth: 2,
            borderColor: undefined
        }));
        this.nodes.update(updates);
    }
    
    async selectNode(nodeId) {
        this.selectedNode = nodeId;
        
        // Get node details
        const node = this.nodes.get(nodeId);
        this.displayNodeDetails(node);
        
        // Get neighbors
        try {
            const response = await fetch('/api/node/neighbors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    node_id: nodeId,
                    depth: 1,
                    min_weight: 0.3
                })
            });
            
            const neighbors = await response.json();
            this.highlightNeighbors(nodeId, neighbors);
            
        } catch (error) {
            console.error('Error getting neighbors:', error);
        }
    }
    
    displayNodeDetails(node) {
        const container = document.getElementById('node-details');
        
        const html = `
            <div class="detail-row">
                <span class="detail-label">Type:</span>
                <span class="detail-value">${node.type}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Content:</span>
                <span class="detail-value">${node.content}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Source:</span>
                <span class="detail-value">${node.source}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Confidence:</span>
                <span class="detail-value">${(node.confidence * 100).toFixed(1)}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Value:</span>
                <span class="detail-value">${node.value || 'N/A'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Tags:</span>
                <span class="detail-value">${(node.tags || []).join(', ')}</span>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    highlightNeighbors(centerNodeId, neighbors) {
        // Implementation for highlighting neighbors
        if (neighbors.neighbors) {
            const neighborIds = neighbors.neighbors.map(n => n.id);
            
            // Highlight center node
            this.nodes.update({
                id: centerNodeId,
                borderWidth: 4,
                borderColor: '#f39c12'
            });
            
            // Highlight neighbors
            neighborIds.forEach(nodeId => {
                this.nodes.update({
                    id: nodeId,
                    borderWidth: 3,
                    borderColor: '#e74c3c'
                });
            });
        }
    }
    
    async performSearch() {
        const query = document.getElementById('search-input').value.trim();
        if (!query) return;
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, limit: 20 })
            });
            
            const results = await response.json();
            this.displaySearchResults(results.results);
            
        } catch (error) {
            console.error('Search failed:', error);
        }
    }
    
    displaySearchResults(results) {
        const container = document.getElementById('search-results');
        
        if (results.length === 0) {
            container.innerHTML = '<p>No results found</p>';
            return;
        }
        
        const html = results.map(node => `
            <div class="search-result-item" onclick="graphViz.focusOnNode('${node.id}')">
                <div class="content">${this.truncateText(node.content, 50)}</div>
                <div class="meta">${node.type} • ${node.source} • ${(node.confidence * 100).toFixed(1)}%</div>
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
            this.updateGraphInfo(`Applied filters: ${data.total_nodes} nodes, ${data.total_edges} edges`);
            
        } catch (error) {
            console.error('Filter application failed:', error);
        }
    }
    
    getFilterValues() {
        // Get selected node types
        const nodeTypes = Array.from(document.querySelectorAll('#node-types-filter input:checked'))
            .map(cb => cb.value);
        
        // Get selected sources
        const sources = Array.from(document.querySelectorAll('#sources-filter input:checked'))
            .map(cb => cb.value);
        
        return {
            node_types: nodeTypes.length > 0 ? nodeTypes : null,
            sources: sources.length > 0 ? sources : null,
            min_confidence: parseFloat(document.getElementById('confidence-slider').value),
            min_weight: parseFloat(document.getElementById('weight-slider').value),
            limit: 100
        };
    }
    
    clearFilters() {
        // Reset all checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
        
        // Reset sliders
        document.getElementById('confidence-slider').value = 0;
        document.getElementById('weight-slider').value = 0.3;
        document.getElementById('confidence-value').textContent = '0.0';
        document.getElementById('weight-value').textContent = '0.3';
        
        // Reset audience select
        document.getElementById('audience-select').value = '';
        
        // Apply filters
        this.applyFilters();
    }
    
    async loadAudienceGraph(audience) {
        try {
            const response = await fetch(`/api/graph/audience/${audience}`);
            const data = await response.json();
            
            this.currentData = data;
            this.updateGraphData(data);
            this.updateGraphInfo(`Audience view: ${audience} (${data.total_nodes} nodes)`);
            
        } catch (error) {
            console.error('Failed to load audience graph:', error);
        }
    }
    
    applyLayout() {
        const layout = document.getElementById('layout-select').value;
        
        const layouts = {
            'force': { physics: { enabled: true } },
            'hierarchical': {
                layout: { hierarchical: { direction: 'UD', sortMethod: 'directed' } },
                physics: { enabled: false }
            },
            'circular': {
                layout: { hierarchical: false },
                physics: { enabled: false }
            },
            'random': {
                layout: { randomSeed: Math.random() },
                physics: { enabled: true }
            }
        };
        
        if (layouts[layout]) {
            this.network.setOptions(layouts[layout]);
            this.updateGraphInfo(`Applied ${layout} layout`);
        }
    }
    
    // Graph control methods
    zoomIn() {
        const scale = this.network.getScale() * 1.2;
        this.network.moveTo({ scale });
    }
    
    zoomOut() {
        const scale = this.network.getScale() * 0.8;
        this.network.moveTo({ scale });
    }
    
    fitToScreen() {
        this.network.fit({ animation: true });
    }
    
    centerGraph() {
        this.network.moveTo({ position: { x: 0, y: 0 }, scale: 1, animation: true });
    }
    
    // Export functionality
    showExportModal() {
        document.getElementById('export-modal').style.display = 'block';
    }
    
    hideExportModal() {
        document.getElementById('export-modal').style.display = 'none';
    }
    
    async downloadData() {
        const format = document.querySelector('input[name="export-format"]:checked').value;
        
        try {
            const response = await fetch(`/api/export/graph?format=${format}`);
            const data = await response.json();
            
            // Create download
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `graph_data.${format}`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.hideExportModal();
            
        } catch (error) {
            console.error('Export failed:', error);
        }
    }
    
    // Utility methods
    updateStats() {
        document.getElementById('total-nodes').textContent = this.currentData.total_nodes || 0;
        document.getElementById('total-edges').textContent = this.currentData.total_edges || 0;
        document.getElementById('visible-nodes').textContent = this.nodes.length;
        document.getElementById('visible-edges').textContent = this.edges.length;
    }
    
    updateGraphInfo(message) {
        document.getElementById('graph-info').textContent = message;
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
    
    showError(message) {
        this.updateGraphInfo(`Error: ${message}`);
        this.showLoading(false);
    }
    
    logActivity(message) {
        const log = document.getElementById('activity-log');
        const time = new Date().toLocaleTimeString();
        
        const activityHtml = `
            <div class="activity-item">
                <span class="activity-text">${message}</span>
                <span class="activity-time">${time}</span>
            </div>
        `;
        
        log.insertAdjacentHTML('afterbegin', activityHtml);
        
        // Keep only last 10 activities
        const items = log.querySelectorAll('.activity-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }
}

// Initialize the graph visualization
let graphViz;
document.addEventListener('DOMContentLoaded', () => {
    graphViz = new GraphVisualization();
}); 