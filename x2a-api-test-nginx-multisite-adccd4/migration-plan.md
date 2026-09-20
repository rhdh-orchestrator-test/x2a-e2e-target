# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and implementing security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file manipulation via Ruby blocks, memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and static content serving
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment focused

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in environment files
- **SSL Certificate Management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations need conversion to ansible.posix.sshd_config module
- **Firewall Rules**: UFW commands need migration to community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration requires Ansible template conversion

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby blocks for Redis configuration file manipulation that need conversion to Ansible lineinfile or replace modules
- **Service Dependencies**: PostgreSQL service must be running before database creation, requiring proper Ansible task ordering and handlers
- **Multi-site SSL**: Dynamic SSL certificate generation for multiple sites needs loop-based Ansible task implementation
- **Git Repository Management**: FastAPI application deployment via git clone needs conversion to ansible.builtin.git module with proper change detection
- **Systemd Service Creation**: Custom systemd service file creation and daemon-reload orchestration requires careful handler implementation

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to SSL and security configurations, but no external service dependencies)
3. **fastapi-tutorial** (highest complexity due to application deployment, database setup, and service orchestration)

### Assumptions

- Target environments will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis will be installed on the same hosts as the applications (no external database servers)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Vagrant development environment will be maintained with Ansible provisioner instead of Chef
- Network connectivity requirements remain the same (HTTP/HTTPS/SSH ports)
- File ownership and permission models can be directly translated from Chef to Ansible
- The existing attribute-based configuration approach will be converted to Ansible variables and group_vars structure