#!/bin/bash

# Slack Integration Setup Script
# This script helps you configure Slack environment variables

echo "🚀 Slack Integration Setup"
echo "=========================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "📝 Please enter your Slack credentials:"
echo ""

# Get Slack Bot Token
echo -n "Enter your Slack Bot Token (xoxb-...): "
read -s SLACK_BOT_TOKEN
echo ""

# Get Slack App Token
echo -n "Enter your Slack App Token (xapp-...): "
read -s SLACK_APP_TOKEN
echo ""

# Get Slack Signing Secret
echo -n "Enter your Slack Signing Secret: "
read -s SLACK_SIGNING_SECRET
echo ""

echo ""
echo "🔧 Updating .env file..."

# Update .env file with the provided values
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/SLACK_BOT_TOKEN=.*/SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN/" .env
    sed -i '' "s/SLACK_APP_TOKEN=.*/SLACK_APP_TOKEN=$SLACK_APP_TOKEN/" .env
    sed -i '' "s/SLACK_SIGNING_SECRET=.*/SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET/" .env
else
    # Linux
    sed -i "s/SLACK_BOT_TOKEN=.*/SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN/" .env
    sed -i "s/SLACK_APP_TOKEN=.*/SLACK_APP_TOKEN=$SLACK_APP_TOKEN/" .env
    sed -i "s/SLACK_SIGNING_SECRET=.*/SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET/" .env
fi

echo "✅ Updated .env file with your Slack credentials"
echo ""

echo "🧪 Testing configuration..."
python test_slack_integration.py

echo ""
echo "📚 Next steps:"
echo "1. Review the SLACK_SETUP.md guide for detailed instructions"
echo "2. Start the backend: cd backend && python app.py"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Test the integration at http://localhost:3000/integrations"
echo ""
echo "🎉 Setup complete!"
