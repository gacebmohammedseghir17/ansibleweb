# Ansible Web Management System

A comprehensive web-based management system for Ansible automation with integrated Linux agent monitoring and Debian server configuration.

## 🚀 Features

### Web Application
- **User Authentication** - Role-based access control with admin privileges
- **Playbook Management** - Execute and manage Ansible playbooks through web interface
- **Real-time Monitoring** - Live server status and resource monitoring
- **Task Scheduling** - Automated task scheduling with cron integration
- **Interactive Chatbot** - AI-powered assistance for operations
- **Comprehensive Logging** - Detailed logs and statistics dashboard
- **Health Monitoring** - System health checks and alerts

### Linux Agent
- **Real-time System Monitoring** - CPU, memory, disk usage tracking
- **Log Collection** - Centralized log forwarding and analysis
- **Remote Management** - Secure communication with main application
- **Resource Tracking** - Performance metrics and alerts

### Ansible Configuration
- **Debian Optimized** - Pre-configured for Debian/Ubuntu systems
- **YAML Configuration** - Clean, readable configuration files
- **Modular Playbooks** - Organized task structure with roles
- **Service Management** - DNS, FTP, logging, and cron automation

## 📁 Project Structure

```
ansible-web/
├── app.py                 # Main Flask application
├── user_management.py     # Authentication system
├── scheduler.py           # Task scheduling
├── cron_manager.py        # Cron job management
├── websocket_server.py    # Real-time communication
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
├── static/               # CSS, JS, assets
├── agent/                # Linux monitoring agent
│   └── linux_agent.py   # Agent application
└── ansible/              # Ansible configuration
    ├── ansible.cfg       # Main config
    ├── inventory/        # Server inventory
    ├── playbooks/        # Automation playbooks
    ├── roles/           # Modular roles
    └── group_vars/      # Group variables
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Ansible 2.9+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ansible-web
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Ansible inventory**
   ```bash
   # Edit ansible/inventory/hosts.yml with your servers
   nano ansible/inventory/hosts.yml
   ```

4. **Start the web application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   - URL: http://localhost:5000
   - Username: `admin`
   - Password: `admin`

## 🔧 Configuration

### Web Application Setup

1. **Security Configuration**
   - Change the default secret key in `app.py`
   - Update default admin credentials in `user_management.py`

2. **Ansible Integration**
   - Configure inventory file: `ansible/inventory/hosts.yml`
   - Customize playbooks in `ansible/playbooks/`
   - Adjust roles in `ansible/roles/`

### Linux Agent Deployment

1. **Copy agent to target servers**
   ```bash
   scp agent/linux_agent.py user@server:/opt/
   ```

2. **Install agent dependencies**
   ```bash
   ssh user@server "pip install psutil requests"
   ```

3. **Configure agent connection**
   - Edit agent configuration to point to web application
   - Set up secure communication credentials

## 📚 Usage

### Web Interface

1. **Login** - Use admin credentials to access the dashboard
2. **Server Management** - Add servers to inventory
3. **Playbook Execution** - Run automation tasks
4. **Monitoring** - View real-time server metrics
5. **Scheduling** - Set up automated tasks

### Available Playbooks

- **DNS Server** - BIND9 configuration and management
- **FTP Server** - vsftpd setup and user management
- **Logging** - Centralized logging with logrotate
- **Cron Jobs** - Automated task scheduling
- **System Ping** - Connectivity testing

### API Endpoints

- `GET /health_check` - System health status
- `POST /run_playbook` - Execute Ansible playbooks
- `GET /api/scheduled_playbooks` - View scheduled tasks
- `POST /api/schedule_playbook` - Schedule new tasks

## 🔒 Security

- **Authentication Required** - All endpoints protected
- **Role-based Access** - Admin-only sensitive operations
- **Secure Communication** - HTTPS recommended for production
- **Input Validation** - Sanitized user inputs

## 🚀 Deployment

### Production Deployment

1. **Use WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Reverse Proxy Setup** (Nginx)
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       location / {
           proxy_pass http://127.0.0.1:5000;
       }
   }
   ```

3. **SSL Configuration**
   - Obtain SSL certificates
   - Configure HTTPS in reverse proxy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation** - Check the `/docs` endpoint in the web interface
- **Issues** - Report bugs via GitHub issues
- **Discussions** - Use GitHub discussions for questions

## 🔄 Changelog

### v1.0.0
- Initial release
- Web-based Ansible management
- Linux agent integration
- Debian configuration templates
- Real-time monitoring
- Task scheduling

---

**Built with ❤️ for DevOps automation**