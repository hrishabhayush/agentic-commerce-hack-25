/**
 * WebSocket Manager for Real-time Graph Collaboration
 * Handles live updates and user interactions
 */

class WebSocketManager {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
        
        this.connect();
    }
    
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket connected');
                this.connected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                
                // Send ping to maintain connection
                this.startPing();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.connected = false;
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.connected = false;
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.attemptReconnect();
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'pong':
                // Handle ping response
                break;
                
            case 'search_activity':
                this.handleSearchActivity(data);
                break;
                
            case 'filter_activity':
                this.handleFilterActivity(data);
                break;
                
            case 'node_selected':
                this.handleNodeSelection(data);
                break;
                
            case 'graph_changed':
                this.handleGraphChange(data);
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    handleSearchActivity(data) {
        if (window.graphViz) {
            window.graphViz.logActivity(`Search: "${data.query}" (${data.results_count} results)`);
        }
    }
    
    handleFilterActivity(data) {
        if (window.graphViz) {
            window.graphViz.logActivity(`Filters applied: ${data.results_count} nodes visible`);
        }
    }
    
    handleNodeSelection(data) {
        if (window.graphViz && data.user !== 'current_user') {
            window.graphViz.logActivity(`User ${data.user} selected node: ${data.node_id}`);
        }
    }
    
    handleGraphChange(data) {
        if (window.graphViz) {
            window.graphViz.logActivity(`Graph updated: ${data.change}`);
        }
    }
    
    send(data) {
        if (this.connected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not connected, message not sent:', data);
        }
    }
    
    startPing() {
        setInterval(() => {
            if (this.connected) {
                this.send({ type: 'ping' });
            }
        }, 30000); // Ping every 30 seconds
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus(false, 'Connection failed');
        }
    }
    
    updateConnectionStatus(connected, message = '') {
        const indicator = document.getElementById('connection-indicator');
        const text = document.getElementById('connection-text');
        
        if (indicator && text) {
            if (connected) {
                indicator.className = 'status-indicator connected';
                text.textContent = 'Connected';
            } else {
                indicator.className = 'status-indicator';
                text.textContent = message || 'Disconnected';
            }
        }
    }
    
    // Public methods for sending specific messages
    notifyNodeSelection(nodeId) {
        this.send({
            type: 'node_selection',
            node_id: nodeId,
            user: 'current_user',
            timestamp: new Date().toISOString()
        });
    }
    
    notifyGraphUpdate(change) {
        this.send({
            type: 'graph_update',
            change: change,
            timestamp: new Date().toISOString()
        });
    }
}

// Initialize WebSocket manager
let wsManager;
document.addEventListener('DOMContentLoaded', () => {
    wsManager = new WebSocketManager();
    
    // Make it globally available
    window.wsManager = wsManager;
}); 