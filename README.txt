# Ansible Web Management System

This project is a comprehensive Ansible web management system with multiple components for server automation and monitoring.

## Project Structure

### Main Application (Root Directory)
The root directory contains the main Flask web application that provides a web interface for managing Ansible operations:

- **app.py** - Main Flask application with web interface
- **user_management.py** - User authentication and role management
- **scheduler.py** - Task scheduling functionality
- **cron_manager.py** - Cron job management
- **websocket_server.py** - WebSocket server for real-time communication
- **templates/** - HTML templates for the web interface
- **static/** - CSS, JavaScript, and other static assets
- **requirements.txt** - Python dependencies

### Agent Subfolder (./agent/)
The agent subfolder contains the Linux agent application that runs on remote servers:

- **linux_agent.py** - Linux monitoring agent that sends server data
- Collects system metrics, logs, and status information
- Communicates with the main web application
- Can be managed remotely through the web interface
- Designed for deployment on Linux servers

### Ansible Subfolder (./ansible/)
The ansible subfolder contains Ansible configuration files optimized for Debian systems:

- **ansible.cfg** - Main Ansible configuration file
- **inventory/hosts.yml** - Server inventory in YAML format
- **playbooks/** - Collection of Ansible playbooks for various tasks:
  - DNS server configuration (dns.yml, dns_*.yml)
  - FTP server setup (ftp.yml, ftp_*.yml)
  - Cron job management (cron.yml)
  - Logging configuration (logging.yml)
  - System ping tests (ping.yml)
- **group_vars/** - Group-specific variables for different server types
- **roles/** - Ansible roles for modular task organization
- **ansible.log** - Ansible execution logs

## Features

### Web Application Features:
- User authentication with role-based access control
- Playbook execution and management
- Real-time server monitoring
- Task scheduling and cron management
- Interactive chatbot for assistance (requires LMStudio)
- Comprehensive logging and statistics
- Health check monitoring

### Agent Features:
- Real-time system monitoring
- Resource usage tracking
- Log collection and forwarding
- Remote management capabilities
- Secure communication with main application

### Ansible Configuration:
- Pre-configured for Debian/Ubuntu systems
- YAML-based configuration files
- Modular playbook structure
- Role-based task organization
- Comprehensive server management tasks

## Default Credentials
- Username: admin
- Password: admin

## Installation
1. Install Python dependencies: pip install -r requirements.txt
2. Configure Ansible inventory in ansible/inventory/hosts.yml
3. Setup LMStudio for AI chatbot:
   - Download and install LMStudio from https://lmstudio.ai/
   - Download a language model (recommended: Llama 2 7B)
   - Start the local server on port 1234
   - Ensure the API is accessible at http://localhost:1234
4. Deploy agents on target Linux servers
5. Run the main application: python app.py
6. Access the web interface at http://localhost:5000

## Usage
1. Log in to the web interface using default credentials
2. Configure your server inventory
3. Deploy agents to target servers
4. Execute playbooks and monitor server status
5. Schedule automated tasks as needed

This system provides a complete solution for Ansible automation with web-based management, remote monitoring agents, and comprehensive server configuration capabilities.