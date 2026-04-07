# PowerShell script to setup SSH key for VPS access using manual commands

$VPS_HOST = "51.222.207.250"
$VPS_USER = "ubuntu"
$VPS_PASSWORD = "Cool220479..@"
$SSH_KEY = "$env:USERPROFILE\.ssh\claude_bot.pub"

Write-Host "🔐 Configuring SSH access to VPS..." -ForegroundColor Cyan
Write-Host "Host: $VPS_HOST"
Write-Host "User: $VPS_USER"
Write-Host ""

# Read the public key
$publicKey = Get-Content $SSH_KEY

Write-Host "📋 Setting up SSH key on VPS..." -ForegroundColor Green

# Create a temporary script file with the commands
$tempScript = @"
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "$publicKey" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "✅ SSH key configured!"
cat ~/.ssh/authorized_keys
"@

# Save temp script to a file
$tempScriptPath = "$env:TEMP\setup-vps-ssh.sh"
$tempScript | Out-File -FilePath $tempScriptPath -Encoding ASCII

Write-Host "⚠️  I'll create a script that you can run with plink or another SSH client" -ForegroundColor Yellow
Write-Host ""

# Try using ssh command interactively
Write-Host "🔧 Attempting to configure SSH key..." -ForegroundColor Yellow

# Use PowerShell's SecureShell if available, otherwise provide instructions
try {
    # Create the command using echo pipe
    $command = "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo `"$publicKey`" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SSH key configured successfully!'"

    Write-Host "Running: ssh $VPS_USER@$VPS_HOST '$command'" -ForegroundColor Cyan
    Write-Host ""

    # Using ssh with the command
    $sshCommand = "ssh $VPS_USER@$VPS_HOST ""$command"""
    Write-Host "Please run this command manually (will prompt for password):" -ForegroundColor Yellow
    Write-Host $sshCommand
    Write-Host ""

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Alternative: Display the exact commands to run manually
Write-Host "📝 Manual setup (if automated doesn't work):" -ForegroundColor Yellow
Write-Host "1. Connect to VPS: ssh $VPS_USER@$VPS_HOST" -ForegroundColor White
Write-Host "2. Run these commands:" -ForegroundColor White
Write-Host "   mkdir -p ~/.ssh" -ForegroundColor White
Write-Host "   chmod 700 ~/.ssh" -ForegroundColor White
Write-Host "   echo `"$publicKey`" >> ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host "   chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host ""
