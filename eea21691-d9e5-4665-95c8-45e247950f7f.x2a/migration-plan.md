# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL certificate generation, multiple virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, security headers, HSTS enforcement, custom nginx.conf template

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, including virtual environment setup and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for custom Redis configuration
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for SSL certificate generation

### Security Considerations

- **SSL/TLS Management**: Self-signed certificate generation for development environments using OpenSSL commands - migrate to community.crypto collection for certificate management
- **Hardcoded Credentials**: 
  - Redis password ('redis_secure_password_123') hardcoded in cache cookbook
  - PostgreSQL credentials ('fastapi_password') hardcoded in fastapi-tutorial cookbook
  - Database connection strings with embedded passwords in environment files
- **SSH Security**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Intrusion prevention with custom jail.local template - migrate to ansible.builtin.template
- **System Hardening**: Custom sysctl security parameters via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Manipulation**: The cache cookbook contains a Ruby block that performs regex-based configuration file editing to remove specific Redis directives - this will need careful translation to Ansible lineinfile or template modules
- **Multi-Service Coordination**: The nginx-multisite cookbook orchestrates multiple services (nginx, fail2ban, ufw, ssh) with complex notification chains - requires careful handler design in Ansible
- **SSL Certificate Dependencies**: Site configuration depends on SSL certificate generation completion - needs proper task ordering and conditional logic
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment requires idempotent Ansible database modules
- **Git Repository Management**: FastAPI application deployment involves git cloning with revision tracking - migrate to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache cookbook** (low risk, minimal dependencies) - straightforward service installation and configuration
2. **fastapi-tutorial cookbook** (moderate complexity) - application deployment with database dependencies
3. **nginx-multisite cookbook** (high complexity, security dependencies) - complex multi-service orchestration with security hardening

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are development placeholders and will be replaced with Ansible Vault or external secret management
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- Systemd is available on target systems for service management
- PostgreSQL version compatibility is maintained between Chef and Ansible deployments
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) remains available and accessible from target systems
- Vagrant development workflow will be replaced with Ansible-based local testing (molecule, vagrant with Ansible provisioner, or direct Ansible execution)