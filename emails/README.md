# 📧 Semantic Email Generation System

This system generates personalized emails for different stakeholder groups using semantic graph data and OpenAI's GPT-4.

## 🚀 Quick Start

1. **Set up your environment:**
   ```bash
   # Copy the example environment file
   cp env.example ../. env
   
   # Edit .env file in the root directory and add your OpenAI API key
   OPENAI_API_KEY=your-actual-api-key-here
   ```

2. **Install dependencies:**
   ```bash
   pip install openai python-dotenv
   ```

3. **Generate emails:**
   ```bash
   python content_generator.py
   ```

## 📁 Generated Files

The system creates personalized .txt email files:
- `investor_update_q1_2024.txt` - Financial metrics for investors
- `customer_newsletter_march.txt` - Feature highlights for customers  
- `team_update_weekly.txt` - Performance metrics for internal team
- `developer_newsletter.txt` - Technical updates for developers
- `growth_milestone_announcement.txt` - Growth celebrations

## 🔒 Security

- ✅ API keys are stored in `.env` file (gitignored)
- ✅ No hardcoded secrets in source code
- ✅ Environment variables loaded securely
- ✅ Safe for version control

## 🎯 Features

- **Semantic Graph Integration**: Uses graph nodes to find relevant data
- **Audience Personalization**: Different tone and focus for each stakeholder
- **Data Traceability**: Each email shows which data sources were used
- **Multiple Formats**: Supports different content types and lengths
- **Full Metadata**: Includes generation stats and confidence scores

## 🔧 Customization

Edit the `email_configs` in `generate_email_suite()` to customize:
- Audience targeting
- Content tone and length
- Focus areas
- Custom filenames

Generated emails include full metadata showing which semantic graph nodes were used for complete transparency and traceability. 