# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, external dependencies on Chef Supermarket cookbooks, and embedded security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, custom Redis config file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificate paths configured but certificate provisioning not automated - implement proper certificate management with community.crypto collection
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Sysctl Security Parameters**: Custom security.conf template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook uses a Ruby block to manually edit Redis config files post-installation - requires custom Ansible tasks with ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Multi-site Nginx Configuration**: Dynamic site generation based on node attributes - implement with Ansible loops and jinja2 templates
- **PostgreSQL Database Provisioning**: SQL commands executed via shell - migrate to community.postgresql collection modules
- **Git Repository Management**: FastAPI app cloned from GitHub - use ansible.builtin.git module with proper idempotency
- **Systemd Service Creation**: Custom service file templates - use ansible.builtin.template and ansible.builtin.systemd modules
- **Chef Solo to Ansible Playbook**: Convert run_list and node attributes to Ansible inventory and group_vars

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational infrastructure)
2. **cache** (low-medium complexity, independent services)
3. **fastapi-tutorial** (medium complexity, depends on database setup)

### Assumptions

- SSL certificates are manually managed or obtained externally (no automated certificate provisioning found in cookbooks)
- The target environment will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- External cookbook dependencies (nginx, memcached, redisio) provide standard configurations that can be replicated with native Ansible modules
- The Vagrant development environment will be replaced with an equivalent Ansible-based local testing setup
- Database credentials and Redis passwords will be migrated to Ansible Vault for proper secrets management
- The current Chef Solo deployment model will be replaced with standard Ansible playbook execution
- Network connectivity and firewall rules assume the same port requirements (22, 80, 443, 6379, 5432, 8000)