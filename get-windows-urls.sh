#!/bin/bash

# Get WSL2 IP address
WSL_IP=$(ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

echo "=================================="
echo "WSL2 Development Server URLs"
echo "=================================="
echo ""
echo "Access from Windows browser:"
echo "  Frontend: http://$WSL_IP:5173"
echo "  Backend:  http://$WSL_IP:8000"
echo "  API Docs: http://$WSL_IP:8000/docs"
echo ""
echo "Access from WSL2 terminal:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Note: WSL2 IP changes when WSL restarts"
echo "=================================="