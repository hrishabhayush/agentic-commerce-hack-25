#!/usr/bin/env python3
"""
Comprehensive Data Generator for Expanded Graph Data
Generates extensive graph data across all categories
"""

import json
import random
import uuid
from datetime import datetime, timedelta
import os

# Data templates by category
TEAM_METRICS_TEMPLATES = [
    "Team velocity increased {value}% this sprint",
    "Code review time decreased by {value}%",
    "Bug resolution time improved {value}%",
    "Team productivity score: {value}/10",
    "Sprint completion rate: {value}%",
    "Developer satisfaction increased {value}%",
    "Code quality metrics improved {value}%",
    "Technical debt reduced by {value}%",
    "Deployment frequency increased {value}%",
    "Mean time to recovery: {value} hours",
    "Feature delivery time reduced {value}%",
    "Team collaboration score: {value}/10"
]

SOCIAL_LISTENING_TEMPLATES = [
    "Brand mention sentiment: {value}% positive",
    "Social media engagement increased {value}%",
    "Competitor analysis shows {value}% market advantage",
    "Hashtag performance improved {value}%",
    "Influencer reach expanded by {value}%",
    "Social media ROI increased {value}%",
    "Customer sentiment score: {value}/10",
    "Viral content reach: {value}K interactions",
    "Brand awareness increased {value}%",
    "Social media crisis response time: {value} minutes",
    "Community engagement rate: {value}%",
    "User-generated content increased {value}%"
]

PRODUCT_ANALYTICS_TEMPLATES = [
    "Feature adoption rate: {value}%",
    "User onboarding completion: {value}%",
    "Product-market fit score: {value}/10",
    "Feature usage analytics show {value}% engagement",
    "User journey conversion improved {value}%",
    "Product stickiness index: {value}%",
    "Time to first value: {value} minutes",
    "Feature discovery rate: {value}%",
    "Product satisfaction score: {value}/10",
    "User workflow efficiency improved {value}%",
    "Product performance metrics: {value}% improvement",
    "Cross-feature usage correlation: {value}%"
]

REVENUE_METRICS_TEMPLATES = [
    "Monthly Recurring Revenue: ${value}K",
    "Customer Acquisition Cost: ${value}",
    "Customer Lifetime Value: ${value}K",
    "Revenue growth rate: {value}%",
    "Churn rate decreased to {value}%",
    "Average Revenue Per User: ${value}",
    "Sales conversion rate: {value}%",
    "Revenue per lead: ${value}",
    "Gross margin improved to {value}%",
    "Net Revenue Retention: {value}%",
    "Cash flow positive by ${value}K",
    "Annual Recurring Revenue: ${value}M"
]

MARKET_INTELLIGENCE_TEMPLATES = [
    "Market share increased to {value}%",
    "Competitive positioning improved {value}%",
    "Market penetration rate: {value}%",
    "Industry growth rate: {value}%",
    "Customer acquisition velocity: {value}% increase",
    "Market opportunity size: ${value}B",
    "Competitive advantage index: {value}/10",
    "Market maturity assessment: {value}%",
    "Regulatory compliance score: {value}%",
    "Market risk assessment: {value}/10",
    "Innovation index ranking: #{value}",
    "Strategic positioning score: {value}/10"
]

CUSTOMER_FEEDBACK_TEMPLATES = [
    "Customer satisfaction score: {value}/10",
    "Net Promoter Score: {value}",
    "Customer effort score: {value}/10",
    "Support ticket resolution improved {value}%",
    "Customer feedback sentiment: {value}% positive",
    "Feature request satisfaction: {value}%",
    "Customer retention rate: {value}%",
    "Support response time: {value} hours",
    "Customer success score: {value}/10",
    "Product feedback quality index: {value}%",
    "Customer advocacy rate: {value}%",
    "User experience rating: {value}/10"
]

# Enhanced data sources by category
DATA_SOURCES = {
    "team_metrics": [
        "jira_api", "github_api", "gitlab_api", "slack_api", "notion_api",
        "linear_api", "asana_api", "azure_devops", "bitbucket_api", "sonarqube_api"
    ],
    "social_listening": [
        "twitter_api", "facebook_api", "instagram_api", "linkedin_api", "tiktok_api",
        "brandwatch_api", "hootsuite_api", "sprout_social", "mention_api", "buzzsumo_api"
    ],
    "product_analytics": [
        "mixpanel_api", "amplitude_api", "google_analytics", "hotjar_api", "fullstory_api",
        "pendo_api", "heap_analytics", "segment_api", "posthog_api", "firebase_analytics"
    ],
    "revenue_metrics": [
        "stripe_api", "chargebee_api", "recurly_api", "salesforce_api", "hubspot_api",
        "pipedrive_api", "quickbooks_api", "xero_api", "profitwell_api", "chargify_api"
    ],
    "market_intelligence": [
        "crunchbase_api", "pitchbook_api", "cbinsights_api", "gartner_api", "forrester_api",
        "statista_api", "bloomberg_api", "reuters_api", "news_api", "google_trends"
    ],
    "customer_feedback": [
        "zendesk_api", "intercom_api", "freshdesk_api", "help_scout", "typeform_api",
        "surveymonkey_api", "trustpilot_api", "g2_api", "capterra_api", "nps_surveys"
    ]
}

# Enhanced tags by category
CATEGORY_TAGS = {
    "team_metrics": [
        "development", "productivity", "velocity", "quality", "collaboration", "efficiency",
        "technical_debt", "deployment", "code_review", "sprint", "agile", "devops"
    ],
    "social_listening": [
        "brand_awareness", "sentiment", "engagement", "viral", "influencer", "hashtag",
        "community", "reputation", "crisis_management", "trending", "reach", "impression"
    ],
    "product_analytics": [
        "adoption", "onboarding", "retention", "engagement", "conversion", "usability",
        "feature_usage", "user_journey", "product_fit", "stickiness", "discovery", "workflow"
    ],
    "revenue_metrics": [
        "mrr", "arr", "ltv", "cac", "churn", "growth", "conversion", "pricing",
        "profitability", "cash_flow", "retention", "upsell", "cross_sell"
    ],
    "market_intelligence": [
        "competitive", "market_share", "positioning", "opportunity", "threat", "trend",
        "disruption", "innovation", "regulation", "growth_potential", "saturation"
    ],
    "customer_feedback": [
        "satisfaction", "nps", "ces", "support", "feedback", "feature_request",
        "bug_report", "user_experience", "advocacy", "testimonial", "review"
    ]
}

def generate_embedding():
    """Generate a random embedding vector"""
    return [random.uniform(-0.15, 0.15) for _ in range(256)]

def generate_audience_relevance():
    """Generate audience relevance scores"""
    audiences = ["investors", "customers", "internal_team", "developer_community"]
    relevance = {audience: random.uniform(0.0, 1.0) for audience in audiences}
    # Ensure at least one audience has high relevance
    max_audience = max(relevance.keys(), key=lambda k: relevance[k])
    relevance[max_audience] = max(relevance[max_audience], 0.4)
    return relevance

def generate_node(category, templates, sources, tags):
    """Generate a node for a specific category"""
    template = random.choice(templates)
    
    if category == "revenue_metrics":
        value = random.randint(10, 5000)  # Larger values for revenue
    elif category == "market_intelligence":
        value = random.randint(1, 100)
    else:
        value = round(random.uniform(5, 100), 1)
    
    content = template.format(value=value)
    
    node_type = "insight" if random.random() < 0.3 else "metric"
    
    return {
        "id": str(uuid.uuid4()),
        "type": node_type,
        "content": content,
        "value": value,
        "timestamp": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
        "confidence": round(random.uniform(0.7, 0.98), 2),
        "source": random.choice(sources),
        "tags": random.sample(tags + ["category_" + category], random.randint(3, 7)),
        "audience_relevance": generate_audience_relevance(),
        "embedding": generate_embedding(),
        "category": category
    }

def generate_edge(source_id, target_id, source_type, target_type):
    """Generate an edge between two nodes"""
    weight = random.uniform(0.3, 0.9)
    semantic_similarity = random.uniform(0.2, 0.8)
    
    return {
        "source_id": source_id,
        "target_id": target_id,
        "relationship_type": random.choice(["relevance", "causation", "correlation", "temporal", "dependency"]),
        "weight": round(weight, 6),
        "confidence": round(random.uniform(0.6, 0.9), 1),
        "semantic_similarity": round(semantic_similarity, 6),
        "metadata": {
            "similarity_score": semantic_similarity,
            "source_types": f"{source_type}-{target_type}",
            "shared_tags": random.sample(["growth", "performance", "user", "engagement"], random.randint(0, 3))
        }
    }

def generate_category_data(category, num_nodes=50):
    """Generate comprehensive data for a specific category"""
    print(f"📊 Generating {num_nodes} nodes for {category}...")
    
    # Get category-specific templates
    if category == "team_metrics":
        templates = TEAM_METRICS_TEMPLATES
    elif category == "social_listening":
        templates = SOCIAL_LISTENING_TEMPLATES
    elif category == "product_analytics":
        templates = PRODUCT_ANALYTICS_TEMPLATES
    elif category == "revenue_metrics":
        templates = REVENUE_METRICS_TEMPLATES
    elif category == "market_intelligence":
        templates = MARKET_INTELLIGENCE_TEMPLATES
    elif category == "customer_feedback":
        templates = CUSTOMER_FEEDBACK_TEMPLATES
    else:
        templates = TEAM_METRICS_TEMPLATES  # fallback
    
    sources = DATA_SOURCES.get(category, DATA_SOURCES["team_metrics"])
    tags = CATEGORY_TAGS.get(category, CATEGORY_TAGS["team_metrics"])
    
    # Generate nodes
    nodes = []
    for i in range(num_nodes):
        node = generate_node(category, templates, sources, tags)
        nodes.append(node)
    
    # Generate edges (create relationships between nodes)
    edges = []
    for i, source_node in enumerate(nodes):
        # Create 3-8 edges per node
        num_edges = random.randint(3, 8)
        
        # Select random target nodes
        possible_targets = [node for node in nodes if node['id'] != source_node['id']]
        targets = random.sample(possible_targets, min(num_edges, len(possible_targets)))
        
        for target_node in targets:
            edge = generate_edge(
                source_node['id'],
                target_node['id'],
                source_node['type'],
                target_node['type']
            )
            edges.append(edge)
    
    return nodes, edges

def save_category_data(category, nodes, edges):
    """Save data for a specific category"""
    # Create category directory if it doesn't exist
    category_dir = f"data/{category}"
    os.makedirs(category_dir, exist_ok=True)
    
    # Prepare nodes data
    nodes_data = {
        "metadata": {
            "total_nodes": len(nodes),
            "category": category,
            "node_types": list(set(node['type'] for node in nodes)),
            "creation_timestamp": datetime.now().isoformat(),
            "expanded": True
        },
        "nodes": nodes
    }
    
    # Prepare edges data
    edges_data = {
        "metadata": {
            "total_edges": len(edges),
            "category": category,
            "creation_timestamp": datetime.now().isoformat(),
            "expanded": True
        },
        "edges": edges
    }
    
    # Save files
    nodes_file = f"{category_dir}/{category}_nodes.json"
    edges_file = f"{category_dir}/{category}_edges.json"
    
    with open(nodes_file, 'w') as f:
        json.dump(nodes_data, f, indent=2)
    
    with open(edges_file, 'w') as f:
        json.dump(edges_data, f, indent=2)
    
    print(f"✅ Saved {len(nodes)} nodes and {len(edges)} edges to {category_dir}/")
    
    return nodes_file, edges_file

def generate_all_expanded_data():
    """Generate expanded data for all categories"""
    categories = [
        "team_metrics",
        "social_listening", 
        "product_analytics",
        "revenue_metrics",
        "market_intelligence",
        "customer_feedback"
    ]
    
    all_nodes = []
    all_edges = []
    
    print("🚀 Starting comprehensive data generation...")
    
    for category in categories:
        # Generate more nodes per category for a richer graph
        nodes_per_category = random.randint(40, 80)
        nodes, edges = generate_category_data(category, nodes_per_category)
        
        # Save category data
        save_category_data(category, nodes, edges)
        
        # Collect for overall stats
        all_nodes.extend(nodes)
        all_edges.extend(edges)
    
    # Generate cross-category relationships
    print("🔗 Generating cross-category relationships...")
    cross_edges = []
    
    for i in range(len(all_nodes)):
        source_node = all_nodes[i]
        
        # Create some cross-category relationships
        if random.random() < 0.3:  # 30% chance for cross-category edge
            possible_targets = [node for node in all_nodes 
                             if node['category'] != source_node['category'] 
                             and node['id'] != source_node['id']]
            
            if possible_targets:
                target_node = random.choice(possible_targets)
                edge = generate_edge(
                    source_node['id'],
                    target_node['id'],
                    source_node['type'],
                    target_node['type']
                )
                cross_edges.append(edge)
    
    all_edges.extend(cross_edges)
    
    # Save consolidated data
    consolidated_nodes = {
        "metadata": {
            "total_nodes": len(all_nodes),
            "total_categories": len(categories),
            "node_types": list(set(node['type'] for node in all_nodes)),
            "categories": categories,
            "creation_timestamp": datetime.now().isoformat(),
            "expanded": True
        },
        "nodes": all_nodes
    }
    
    consolidated_edges = {
        "metadata": {
            "total_edges": len(all_edges),
            "cross_category_edges": len(cross_edges),
            "creation_timestamp": datetime.now().isoformat(),
            "expanded": True
        },
        "edges": all_edges
    }
    
    # Save consolidated files
    with open('data/consolidated_nodes.json', 'w') as f:
        json.dump(consolidated_nodes, f, indent=2)
    
    with open('data/consolidated_edges.json', 'w') as f:
        json.dump(consolidated_edges, f, indent=2)
    
    print(f"\n🎉 Data generation complete!")
    print(f"📊 Total: {len(all_nodes)} nodes, {len(all_edges)} edges")
    print(f"🔗 Cross-category relationships: {len(cross_edges)}")
    print(f"📁 Data saved in individual category folders and consolidated files")
    
    return len(all_nodes), len(all_edges)

if __name__ == "__main__":
    total_nodes, total_edges = generate_all_expanded_data()
    print(f"\n✨ Your expanded graph now has {total_nodes} nodes and {total_edges} edges!")
    print(f"🌐 Ready for an impressive visualization!") 