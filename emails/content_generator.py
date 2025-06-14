#!/usr/bin/env python3
"""
Agentic Commerce Content Generation System
Uses semantic graph to generate personalized content for different audiences
"""

import json
import os
from typing import List, Dict, Any, Optional
import openai
from dataclasses import dataclass
import networkx as nx
from pathlib import Path

# Load environment variables from .env file in root directory
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")
    print("   Install with: pip install python-dotenv")

# OpenAI API key should be set as environment variable
# Set it with: export OPENAI_API_KEY="your-api-key-here"
# Or create a .env file in root with: OPENAI_API_KEY=your-api-key-here
if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in .env file or export it.")

@dataclass
class ContentRequest:
    """Represents a content generation request"""
    audience: str  # investors, customers, internal_team, developer_community
    content_type: str  # email, report, social_post, blog_article, presentation
    tone: str  # professional, casual, technical, marketing
    length: str  # short, medium, long
    focus_areas: List[str] = None  # specific topics to emphasize
    context: str = ""  # additional context

class SemanticContentGenerator:
    """AI-powered content generator using semantic graph knowledge"""
    
    def __init__(self, graph_dir: str = "../graphs"):
        self.graph_dir = Path(graph_dir)
        self.client = openai.OpenAI()
        
        # Load graph data
        self.nodes_data = self._load_json(self.graph_dir / "nodes" / "flowmetrics_nodes.json")
        self.edges_data = self._load_json(self.graph_dir / "edges" / "flowmetrics_edges.json")
        self.summary_data = self._load_json(self.graph_dir / "processed" / "graph_summary.json")
        
        # Build knowledge graph
        self.knowledge_graph = self._build_knowledge_graph()
        
        # Define audience preferences
        self.audience_config = {
            "investors": {
                "preferred_metrics": ["revenue", "growth", "mrr", "customers", "market"],
                "tone_keywords": ["strategic", "financial", "scalable", "market opportunity"],
                "focus": "financial performance and growth potential"
            },
            "customers": {
                "preferred_metrics": ["features", "satisfaction", "performance", "reliability"],
                "tone_keywords": ["beneficial", "improved", "enhanced", "value"],
                "focus": "product benefits and improvements"
            },
            "internal_team": {
                "preferred_metrics": ["performance", "efficiency", "goals", "team", "operations"],
                "tone_keywords": ["achievement", "progress", "objectives", "collaboration"],
                "focus": "operational excellence and team performance"
            },
            "developer_community": {
                "preferred_metrics": ["technical", "api", "integration", "features", "development"],
                "tone_keywords": ["technical", "implementation", "developer-friendly", "innovation"],
                "focus": "technical capabilities and developer experience"
            }
        }
    
    def _load_json(self, filepath: Path) -> Dict:
        """Load JSON data from file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}
    
    def _build_knowledge_graph(self) -> nx.Graph:
        """Build NetworkX graph from semantic data"""
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
                similarity=edge['semantic_similarity']
            )
        
        return G
    
    def find_relevant_nodes(self, audience: str, focus_areas: List[str] = None) -> List[Dict]:
        """Find graph nodes most relevant to specific audience and focus areas"""
        relevant_nodes = []
        audience_config = self.audience_config.get(audience, {})
        preferred_metrics = audience_config.get("preferred_metrics", [])
        
        for node_id in self.knowledge_graph.nodes():
            node_data = self.knowledge_graph.nodes[node_id]
            relevance_score = 0
            
            # Score based on audience preferences
            for metric in preferred_metrics:
                if any(metric.lower() in tag.lower() for tag in node_data['tags']):
                    relevance_score += 0.3
                if metric.lower() in node_data['content'].lower():
                    relevance_score += 0.2
            
            # Score based on focus areas
            if focus_areas:
                for focus in focus_areas:
                    if focus.lower() in node_data['content'].lower():
                        relevance_score += 0.4
                    if any(focus.lower() in tag.lower() for tag in node_data['tags']):
                        relevance_score += 0.3
            
            # Score based on node centrality (importance in network)
            degree_centrality = nx.degree_centrality(self.knowledge_graph)[node_id]
            relevance_score += degree_centrality * 0.2
            
            if relevance_score > 0.2:  # Threshold for relevance
                relevant_nodes.append({
                    'node_id': node_id,
                    'content': node_data['content'],
                    'type': node_data['type'],
                    'source': node_data['source'],
                    'tags': node_data['tags'],
                    'confidence': node_data['confidence'],
                    'relevance_score': relevance_score
                })
        
        # Sort by relevance score
        relevant_nodes.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_nodes[:8]  # Return top 8 most relevant
    
    def build_context_prompt(self, request: ContentRequest) -> str:
        """Build comprehensive context prompt for AI generation"""
        relevant_nodes = self.find_relevant_nodes(request.audience, request.focus_areas)
        audience_config = self.audience_config.get(request.audience, {})
        
        # Build context from relevant nodes
        knowledge_context = "\n".join([
            f"- {node['content']} (Source: {node['source']}, Confidence: {node['confidence']:.2f})"
            for node in relevant_nodes
        ])
        
        # Build comprehensive prompt
        prompt = f"""
You are an expert content generator for FlowMetrics, a B2B SaaS analytics platform for e-commerce businesses. 

COMPANY CONTEXT:
- Series A stage, $2.8M ARR, 25% QoQ growth
- 450+ customers, $199-$999/month pricing tiers  
- 25 employees, serving e-commerce analytics market

TARGET AUDIENCE: {request.audience}
CONTENT TYPE: {request.content_type}
TONE: {request.tone}
LENGTH: {request.length}
FOCUS: {audience_config.get('focus', 'general business performance')}

RELEVANT DATA INSIGHTS:
{knowledge_context}

AUDIENCE PREFERENCES:
- Key interests: {', '.join(audience_config.get('preferred_metrics', []))}
- Tone keywords: {', '.join(audience_config.get('tone_keywords', []))}

ADDITIONAL CONTEXT: {request.context}

REQUIREMENTS:
1. Use the provided data insights as supporting evidence
2. Tailor the message specifically for {request.audience}
3. Maintain a {request.tone} tone throughout
4. Make it {request.length} in length
5. Include specific metrics and numbers from the data
6. Make it actionable and engaging
7. Ensure accuracy - only use provided data points

Generate compelling {request.content_type} content:
"""
        return prompt
    
    def generate_content(self, request: ContentRequest) -> Dict[str, Any]:
        """Generate content using OpenAI API and semantic graph context"""
        try:
            # Build context-rich prompt
            prompt = self.build_context_prompt(request)
            
            # Get relevant nodes for traceability
            relevant_nodes = self.find_relevant_nodes(request.audience, request.focus_areas)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert B2B SaaS content writer with deep understanding of analytics and e-commerce."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000 if request.length == "long" else 1000 if request.length == "medium" else 500,
                temperature=0.7
            )
            
            generated_content = response.choices[0].message.content
            
            return {
                "success": True,
                "content": generated_content,
                "metadata": {
                    "audience": request.audience,
                    "content_type": request.content_type,
                    "tone": request.tone,
                    "length": request.length,
                    "focus_areas": request.focus_areas,
                    "relevant_nodes_count": len(relevant_nodes),
                    "data_sources": list(set([node['source'] for node in relevant_nodes])),
                    "confidence_scores": [node['confidence'] for node in relevant_nodes],
                    "model_used": "gpt-4"
                },
                "source_nodes": relevant_nodes,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def generate_multi_audience_campaign(self, campaign_theme: str, content_type: str = "email") -> Dict[str, Any]:
        """Generate coordinated content for all audiences around a theme"""
        results = {}
        
        for audience in self.audience_config.keys():
            request = ContentRequest(
                audience=audience,
                content_type=content_type,
                tone="professional",
                length="medium",
                focus_areas=[campaign_theme],
                context=f"Part of coordinated campaign about {campaign_theme}"
            )
            
            results[audience] = self.generate_content(request)
        
        return results
    
    def save_email_as_txt(self, content_result: Dict, custom_filename: str = None):
        """Save generated email content as .txt file"""
        if not content_result["success"]:
            print(f"❌ Cannot save failed content generation: {content_result.get('error', 'Unknown error')}")
            return
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename based on content metadata
        metadata = content_result["metadata"]
        if custom_filename:
            filename = custom_filename
        else:
            filename = f"{metadata['audience']}_{metadata['content_type']}_{timestamp}.txt"
        
        # Create email header with metadata
        email_header = f"""
===============================================
📧 EMAIL GENERATED BY SEMANTIC GRAPH SYSTEM
===============================================
Audience: {metadata['audience'].title()}
Content Type: {metadata['content_type'].title()}
Tone: {metadata['tone'].title()}
Length: {metadata['length'].title()}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 DATA SOURCES USED:
{', '.join(metadata['data_sources'])}

🎯 FOCUS AREAS:
{', '.join(metadata.get('focus_areas', ['General'])) if metadata.get('focus_areas') else 'General'}

🔗 RELEVANT NODES: {metadata['relevant_nodes_count']}
💬 TOKENS USED: {content_result['tokens_used']}
===============================================

"""
        
        # Create the complete email content
        full_email = email_header + content_result["content"]
        
        # Save as .txt file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_email)
        
        print(f"✅ Email saved as: {filename}")
        print(f"📝 Content length: {len(content_result['content'])} characters")
        return filename
    
    def save_content(self, content_result: Dict, filename: str = None):
        """Save generated content to file (legacy JSON format)"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_content_{timestamp}.json"
        
        output_dir = Path("generated_content")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w') as f:
            json.dump(content_result, f, indent=2, default=str)
        
        print(f"✅ Content saved to {output_dir / filename}")


def generate_email_suite():
    """Generate a complete suite of emails for different audiences"""
    print("🚀 Initializing Semantic Email Generator...")
    print("📧 Generating emails for all stakeholder groups using semantic graph data...")
    
    generator = SemanticContentGenerator()
    
    # Email configurations for different audiences
    email_configs = [
        {
            "name": "Investor Update",
            "request": ContentRequest(
                audience="investors",
                content_type="email",
                tone="professional",
                length="medium",
                focus_areas=["growth", "revenue", "mrr", "market"],
                context="Q1 2024 investor update highlighting strong growth metrics and market performance"
            ),
            "filename": "investor_update_q1_2024.txt"
        },
        {
            "name": "Customer Newsletter",
            "request": ContentRequest(
                audience="customers",
                content_type="email",
                tone="marketing",
                length="medium",
                focus_areas=["features", "satisfaction", "performance"],
                context="Monthly customer newsletter highlighting new features and improvements"
            ),
            "filename": "customer_newsletter_march.txt"
        },
        {
            "name": "Team Performance Update",
            "request": ContentRequest(
                audience="internal_team",
                content_type="email",
                tone="professional",
                length="medium",
                focus_areas=["performance", "goals", "team"],
                context="Weekly team update highlighting achievements and operational metrics"
            ),
            "filename": "team_update_weekly.txt"
        },
        {
            "name": "Developer Community",
            "request": ContentRequest(
                audience="developer_community",
                content_type="email",
                tone="technical",
                length="medium",
                focus_areas=["integration", "api", "technical"],
                context="Developer newsletter about new API features and integration capabilities"
            ),
            "filename": "developer_newsletter.txt"
        },
        {
            "name": "Growth Milestone Announcement",
            "request": ContentRequest(
                audience="customers",
                content_type="email",
                tone="marketing",
                length="short",
                focus_areas=["growth", "users", "engagement"],
                context="Celebrating reaching 1,247 daily active users milestone"
            ),
            "filename": "growth_milestone_announcement.txt"
        }
    ]
    
    generated_emails = []
    
    for config in email_configs:
        print(f"\n📝 Generating: {config['name']}...")
        
        # Generate content
        result = generator.generate_content(config["request"])
        
        if result["success"]:
            # Save as .txt file
            filename = generator.save_email_as_txt(result, config["filename"])
            generated_emails.append({
                "name": config["name"],
                "filename": filename,
                "audience": config["request"].audience,
                "success": True,
                "data_sources": result["metadata"]["data_sources"],
                "nodes_used": result["metadata"]["relevant_nodes_count"],
                "tokens": result["tokens_used"]
            })
            print(f"   ✅ {config['name']} saved successfully")
        else:
            print(f"   ❌ Failed: {result['error']}")
            generated_emails.append({
                "name": config["name"],
                "success": False,
                "error": result["error"]
            })
    
    # Print summary
    print("\n" + "="*60)
    print("📧 EMAIL GENERATION SUMMARY")
    print("="*60)
    
    successful_emails = [e for e in generated_emails if e.get("success", False)]
    failed_emails = [e for e in generated_emails if not e.get("success", False)]
    
    print(f"✅ Successfully generated: {len(successful_emails)} emails")
    print(f"❌ Failed: {len(failed_emails)} emails")
    
    if successful_emails:
        print("\n📁 Generated Files:")
        for email in successful_emails:
            print(f"   • {email['filename']} ({email['audience']} - {email['nodes_used']} data points)")
    
    if failed_emails:
        print("\n❌ Failed Generations:")
        for email in failed_emails:
            print(f"   • {email['name']}: {email.get('error', 'Unknown error')}")
    
    return generator, generated_emails


if __name__ == "__main__":
    generator, generated_emails = generate_email_suite() 