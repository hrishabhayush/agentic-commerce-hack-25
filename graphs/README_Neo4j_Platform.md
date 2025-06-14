# 🎯 Agentic Commerce Graph Visualization Platform

A professional graph visualization platform inspired by [Linkurious](https://linkurious.com/decision-intelligence-platform-graph-visualization/), built with Neo4j and modern web technologies for powerful, intuitive graph analysis.

## 🌟 Features

### 🔍 **Powerful Graph Database**
- **Neo4j Integration**: Professional graph database backend
- **High Performance**: Optimized queries with constraints and indexes
- **Scalable**: Handles large datasets efficiently
- **Real-time**: Live data updates and collaboration

### 🎨 **Intuitive Visualization**
- **Interactive Interface**: Click, drag, zoom, and explore
- **Multiple Layouts**: Force-directed, hierarchical, circular, random
- **Smart Styling**: Node size based on confidence, colors by type
- **Responsive Design**: Works on desktop, tablet, and mobile

### 🔎 **Advanced Search & Filtering**
- **Full-text Search**: Find nodes by content, source, or tags
- **Multi-dimensional Filters**: Node types, sources, confidence, weight
- **Audience Focus**: Investor, customer, internal team, developer views
- **No-code Query Builder**: Visual filter construction

### 📊 **Analytics & Insights**
- **Graph Statistics**: Real-time metrics and overview
- **Node Relationships**: Explore neighbors and connections
- **Centrality Analysis**: Identify most connected nodes
- **Data Export**: JSON, CSV, GraphML formats

### 🤝 **Collaboration Features**
- **Real-time Updates**: See other users' activities
- **WebSocket Integration**: Live collaboration
- **Activity Logging**: Track all user interactions
- **Shared Workspaces**: Team-based exploration

## 🚀 Quick Start

### Prerequisites

1. **Neo4j Database**
   ```bash
   # Download Neo4j Desktop from neo4j.com
   # OR install via Docker:
   docker run --name neo4j \
     -p7474:7474 -p7687:7687 \
     -d \
     -v neo4j_data:/data \
     -v neo4j_logs:/logs \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

2. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Installation & Setup

1. **Clone and navigate to graphs directory**
   ```bash
   cd graphs/
   ```

2. **Run the setup script**
   ```bash
   python setup_graph_platform.py
   ```

3. **Access the platform**
   - Dashboard: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

## 🎮 Platform Features

### Main Interface

The platform provides a professional, three-panel layout:

1. **Left Panel**: Search, filters, statistics, layout controls
2. **Center Panel**: Interactive graph visualization
3. **Right Panel**: Node details, analytics, activity log

### Core Capabilities

#### 🔍 **Search & Discovery**
- **Semantic Search**: Find nodes by content similarity
- **Filter Combinations**: Combine multiple filter criteria
- **Instant Results**: Real-time search as you type
- **Result Highlighting**: Visual focus on search results

#### 🎛️ **Advanced Filtering**
- **Node Type Filter**: Metrics, insights, or custom types
- **Source Filter**: Filter by data source (APIs, databases, files)
- **Confidence Range**: Show only high-confidence data
- **Relationship Weight**: Filter weak or strong connections
- **Audience Focus**: Stakeholder-specific views

#### 📈 **Graph Analytics**
- **Centrality Analysis**: Most connected and influential nodes
- **Relationship Strength**: Identify strongest connections
- **Tag Distribution**: Popular topics and themes
- **Network Statistics**: Comprehensive graph metrics

#### 🎨 **Visualization Options**
- **Force-Directed**: Natural clustering and grouping
- **Hierarchical**: Tree-like structure with clear hierarchy
- **Circular**: Balanced circular arrangement
- **Custom Layouts**: Algorithm-based positioning

## 📋 API Reference

The platform provides a comprehensive REST API:

### Core Endpoints

```http
GET    /api/health                    # Health check
GET    /api/overview                  # Graph statistics
POST   /api/search                    # Node search
POST   /api/graph/filtered            # Filtered graph data
GET    /api/graph/audience/{audience} # Audience-specific view
POST   /api/node/neighbors            # Node relationships
GET    /api/analytics                 # Advanced analytics
GET    /api/export/graph              # Data export
```

### Example API Usage

#### Search Nodes
```bash
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "user growth", "limit": 20}'
```

#### Apply Filters
```bash
curl -X POST "http://localhost:8000/api/graph/filtered" \
     -H "Content-Type: application/json" \
     -d '{
       "node_types": ["metric"],
       "min_confidence": 0.8,
       "min_weight": 0.5,
       "limit": 100
     }'
```

#### Get Audience View
```bash
curl "http://localhost:8000/api/graph/audience/investors?limit=50"
```

## 🛠️ Advanced Configuration

### Neo4j Customization

Edit `neo4j_client.py` to customize:

```python
# Custom connection settings
client = Neo4jGraphClient(
    uri="bolt://your-neo4j-server:7687",
    username="your-username",
    password="your-password"
)

# Custom node labels and properties
client.load_nodes_with_custom_schema(your_schema)
```

### Frontend Customization

Modify `static/css/graph_styles.css` for styling:

```css
/* Custom node colors */
.node-metric { color: #your-color; }
.node-insight { color: #your-color; }

/* Custom layout */
.sidebar { width: 400px; }
.graph-area { background: #your-background; }
```

### API Extensions

Add custom endpoints in `graph_api.py`:

```python
@app.get("/api/custom/endpoint")
async def custom_analysis():
    # Your custom analytics logic
    return {"custom": "data"}
```

## 🔧 Troubleshooting

### Common Issues

#### Neo4j Connection Failed
```
❌ Neo4j connection failed: ServiceUnavailable
```
**Solution**: Ensure Neo4j is running and accessible
- Check if Neo4j service is started
- Verify connection settings (host, port, credentials)
- Test connection with Neo4j Browser

#### Missing Dependencies
```
❌ Missing dependencies: No module named 'neo4j'
```
**Solution**: Install required packages
```bash
pip install -r requirements.txt
```

#### Graph Data Not Loading
```
❌ Graph data files not found
```
**Solution**: Ensure data files exist
- Check `nodes/flowmetrics_nodes.json`
- Check `edges/flowmetrics_edges.json`
- Verify file paths and permissions

#### Frontend Assets Missing
```
❌ Static files not found
```
**Solution**: Run setup script to create missing files
```bash
python setup_graph_platform.py
```

### Performance Optimization

#### For Large Datasets
1. **Increase Neo4j Memory**:
   ```
   # In neo4j.conf
   dbms.memory.heap.initial_size=4G
   dbms.memory.heap.max_size=8G
   ```

2. **Optimize Queries**:
   ```python
   # Use LIMIT in queries
   # Create appropriate indexes
   # Use EXPLAIN to analyze query performance
   ```

3. **Frontend Optimization**:
   ```javascript
   // Reduce initial load size
   limit: 50
   
   // Use clustering for many nodes
   options.clustering = { enabled: true }
   ```

## 🎯 Use Cases

### 📈 **For Business Analytics**
- Explore customer behavior patterns
- Analyze product feature relationships
- Track KPI correlations and trends
- Generate stakeholder-specific insights

### 🔬 **For Data Science**
- Visualize ML model relationships
- Explore feature importance networks
- Analyze data pipeline dependencies
- Debug model performance issues

### 🏢 **For Enterprise Teams**
- Share interactive dashboards
- Collaborate on data exploration
- Export insights for presentations
- Monitor real-time business metrics

### 👥 **For Stakeholder Communication**
- Investor-focused financial metrics
- Customer-centric product insights
- Developer-oriented technical graphs
- Executive summary dashboards

## 🔮 Roadmap

### Upcoming Features
- [ ] Advanced graph algorithms (PageRank, Community Detection)
- [ ] Custom visualization themes and branding
- [ ] Scheduled data updates and alerts
- [ ] Advanced export options (PowerBI, Tableau)
- [ ] Machine learning integration
- [ ] Multi-tenant support

### Integrations
- [ ] Slack/Teams notifications
- [ ] Jupyter notebook widgets
- [ ] REST API connectors
- [ ] Cloud storage exports

## 📞 Support

For questions, issues, or feature requests:

1. **Check Documentation**: Comprehensive API docs at `/docs`
2. **Review Examples**: Sample queries and usage patterns
3. **Debug Mode**: Enable detailed logging for troubleshooting
4. **Performance Monitoring**: Use built-in analytics for optimization

---

## 📊 Comparison with Other Platforms

| Feature | Our Platform | Linkurious | Gephi | Cytoscape |
|---------|-------------|------------|-------|-----------|
| **Neo4j Integration** | ✅ Native | ✅ Yes | ❌ No | ❌ No |
| **Web-based** | ✅ Yes | ✅ Yes | ❌ Desktop | ❌ Desktop |
| **Real-time Collaboration** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Custom Filters** | ✅ Advanced | ✅ Yes | ⚠️ Basic | ⚠️ Basic |
| **API Access** | ✅ Full REST API | ✅ Yes | ❌ No | ⚠️ Limited |
| **Open Source** | ✅ Yes | ❌ Commercial | ✅ Yes | ✅ Yes |
| **Audience Views** | ✅ Built-in | ⚠️ Custom | ❌ No | ❌ No |

---

**Built with ❤️ for the Agentic Commerce project** 