#!/bin/bash
# Setup SSH key for VPS access

VPS_HOST="51.222.207.250"
VPS_USER="ubuntu"
VPS_PORT="22"
SSH_KEY="$HOME/.ssh/claude_bot"

echo "🔐 Configuring SSH access to VPS..."
echo "Host: $VPS_HOST"
echo "User: $VPS_USER"
echo "Port: $VPS_PORT"
echo ""

# Copy SSH key using password
echo "📋 Copying SSH key to VPS..."
echo "You'll need to enter your VPS password when prompted"
echo ""

ssh-copy-id -i "$SSH_KEY.pub" -p "$VPS_PORT" "$VPS_USER@$VPS_HOST"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSH key configured successfully!"
    echo ""
    echo "Testing connection..."
    ssh -p "$VPS_PORT" -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" "echo '✅ SSH connection successful!'"
    echo ""
    echo "You can now run: bash deploy.sh"
else
    echo ""
    echo "❌ Failed to copy SSH key"
    echo "Try manually:"
    echo "cat ~/.ssh/claude_bot.pub | ssh -p 22 ubuntu@51.222.207.250 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'"
fi
