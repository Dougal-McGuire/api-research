#!/bin/bash

# Development environment aliases for api-research
# Source this file to load aliases: source dev-aliases.sh

alias dev-start='./start-dev.sh'
alias dev-stop='./stop-dev.sh'
alias dev-logs='docker compose -f docker-compose.dev.yml logs -f'
alias dev-status='docker compose -f docker-compose.dev.yml ps'
alias dev-urls='./get-windows-urls.sh'
alias dev-restart='./stop-dev.sh && ./start-dev.sh'
alias dev-build='docker compose -f docker-compose.dev.yml build'
alias dev-shell-web='docker compose -f docker-compose.dev.yml exec web bash'
alias dev-shell-frontend='docker compose -f docker-compose.dev.yml exec frontend sh'

echo "🚀 Development aliases loaded:"
echo "  dev-start     - Start development environment"
echo "  dev-stop      - Stop development environment"
echo "  dev-logs      - View container logs"
echo "  dev-status    - Show container status"
echo "  dev-urls      - Show access URLs"
echo "  dev-restart   - Restart development environment"
echo "  dev-build     - Rebuild containers"
echo "  dev-shell-web - Open shell in web container"
echo "  dev-shell-frontend - Open shell in frontend container"