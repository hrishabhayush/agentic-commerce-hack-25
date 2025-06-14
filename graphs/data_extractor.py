"""
Data extraction module for FlowMetrics graph builder
Converts raw JSON data into structured data points for the semantic graph
"""

from typing import List, Dict, Any

class FlowMetricsDataExtractor:
    """Extract structured data points from FlowMetrics data sources"""
    
    def extract_data_points(self, data_list: List[Dict]) -> List[Dict]:
        """Extract individual data points that can become nodes"""
        print("🔍 Extracting data points for graph nodes...")
        
        data_points = []
        
        for data in data_list:
            source_file = data.get('_file_source', 'unknown')
            source_api = data.get('source', 'unknown')
            
            # Extract different types of data points based on file type
            if 'daily_active_users' in source_file:
                data_points.extend(self._extract_dau_points(data, source_api))
            elif 'feature_adoption' in source_file:
                data_points.extend(self._extract_feature_points(data, source_api))
            elif 'monthly_recurring_revenue' in source_file:
                data_points.extend(self._extract_revenue_points(data, source_api))
            elif 'support_tickets' in source_file:
                data_points.extend(self._extract_support_points(data, source_api))
            elif 'competitor_analysis' in source_file:
                data_points.extend(self._extract_market_points(data, source_api))
            elif 'brand_mentions' in source_file:
                data_points.extend(self._extract_social_points(data, source_api))
            elif 'internal_kpis' in source_file:
                data_points.extend(self._extract_team_points(data, source_api))
        
        print(f"📋 Extracted {len(data_points)} data points")
        return data_points
    
    def _extract_dau_points(self, data: Dict, source: str) -> List[Dict]:
        """Extract DAU-related data points"""
        points = []
        
        # Main DAU growth metric
        points.append({
            "type": "metric",
            "content": f"Daily Active Users grew {data['metrics']['growth_rate']:.1f}% to {data['metrics']['current_dau']} users",
            "value": data['metrics']['growth_rate'],
            "source": source,
            "tags": ["growth", "users", "engagement", "monthly"],
            "confidence": 0.95,
            "timestamp": "2024-01-15",
            "metadata": {
                "metric_type": "dau_growth",
                "current_value": data['metrics']['current_dau'],
                "previous_value": data['metrics']['previous_period_dau']
            }
        })
        
        # Extract insights
        for insight in data.get('insights', []):
            points.append({
                "type": "insight",
                "content": insight['content'],
                "value": insight.get('supporting_data', ''),
                "source": source,
                "tags": ["behavior", "product", "engagement"],
                "confidence": insight['confidence'],
                "timestamp": "2024-01-15",
                "metadata": {
                    "insight_type": insight['type']
                }
            })
        
        return points
    
    def _extract_feature_points(self, data: Dict, source: str) -> List[Dict]:
        """Extract feature adoption data points"""
        points = []
        
        for feature in data.get('features', []):
            points.append({
                "type": "metric",
                "content": f"{feature['feature_name']} has {feature['adoption_metrics']['adoption_rate']:.1f}% adoption rate",
                "value": feature['adoption_metrics']['adoption_rate'],
                "source": source,
                "tags": ["features", "adoption", feature['feature_name'].replace('_', '-')],
                "confidence": 0.88,
                "timestamp": feature['launch_date'],
                "metadata": {
                    "feature_name": feature['feature_name'],
                    "business_impact": feature['business_impact']
                }
            })
        
        return points
    
    def _extract_revenue_points(self, data: Dict, source: str) -> List[Dict]:
        """Extract revenue-related data points"""
        points = []
        
        # MRR growth
        points.append({
            "type": "metric",
            "content": f"Monthly Recurring Revenue grew {data['current_metrics']['mrr_growth_qoq']:.1f}% QoQ to ${data['current_metrics']['mrr_current']:,}",
            "value": data['current_metrics']['mrr_growth_qoq'],
            "source": source,
            "tags": ["revenue", "growth", "mrr", "quarterly"],
            "confidence": 0.96,
            "timestamp": "2024-03-31",
            "metadata": {
                "metric_type": "mrr_growth",
                "current_mrr": data['current_metrics']['mrr_current']
            }
        })
        
        return points
    
    def _extract_support_points(self, data: Dict, source: str) -> List[Dict]:
        """Extract customer support data points"""
        points = []
        
        # Support satisfaction
        points.append({
            "type": "metric",
            "content": f"Customer support satisfaction: {data['summary_metrics']['customer_satisfaction_score']:.1f}/5.0",
            "value": data['summary_metrics']['customer_satisfaction_score'],
            "source": source,
            "tags": ["support", "satisfaction", "customer-experience"],
            "confidence": 0.89,
            "timestamp": "2024-01-31",
            "metadata": {
                "metric_type": "support_satisfaction"
            }
        })
        
        return points
    
    def _extract_market_points(self, data: Dict, source: str) -> List[Dict]:
        """Extract market intelligence data points"""
        points = []
        
        # Market opportunities
        for opportunity in data.get('market_opportunities', []):
            points.append({
                "type": "insight",
                "content": f"{opportunity['opportunity'].replace('_', ' ').title()}: ${opportunity['expected_arr_impact']:,} potential ARR",
                "value": opportunity['expected_arr_impact'],
                "source": source,
                "tags": ["opportunity", "expansion", opportunity['opportunity'].replace('_', '-')],
                "confidence": 0.80,
                "timestamp": "2024-01-30",
                "metadata": {
                    "opportunity_type": opportunity['opportunity'],
                    "market_size": opportunity['market_size']
                }
            })
        
        return points
    
    def _extract_social_points(self, data: Dict, source: str) -> List[Dict]:
        """Extract social listening data points"""
        points = []
        
        # Overall sentiment
        points.append({
            "type": "metric",
            "content": f"Brand sentiment: {data['summary_metrics']['net_sentiment_score']:.1f}% across {data['summary_metrics']['total_mentions']} mentions",
            "value": data['summary_metrics']['net_sentiment_score'],
            "source": source,
            "tags": ["sentiment", "brand", "social"],
            "confidence": 0.87,
            "timestamp": "2024-01-31",
            "metadata": {
                "total_mentions": data['summary_metrics']['total_mentions']
            }
        })
        
        return points
    
    def _extract_team_points(self, data: Dict, source: str) -> List[Dict]:
        """Extract team performance data points"""
        points = []
        
        # Overall team metrics
        points.append({
            "type": "metric",
            "content": f"Team size: {data['team_overview']['total_employees']} employees with {data['team_overview']['employee_satisfaction']:.1f}/5.0 satisfaction",
            "value": data['team_overview']['total_employees'],
            "source": source,
            "tags": ["team", "headcount", "satisfaction"],
            "confidence": 0.92,
            "timestamp": "2024-03-31",
            "metadata": {
                "satisfaction": data['team_overview']['employee_satisfaction']
            }
        })
        
        return points 