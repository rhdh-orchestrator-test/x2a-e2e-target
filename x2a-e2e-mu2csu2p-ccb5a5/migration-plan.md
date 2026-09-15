# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific nginx configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant environment

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local development focus)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate using community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate using ansible.builtin.template module
- **Database Credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault with postgresql_* modules

### Technical Challenges

- **Redis Configuration Patching**: Complex ruby_block that modifies Redis config file post-installation requires custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL Management**: Dynamic certificate generation per site requires Ansible loops and conditional logic
- **Service Dependencies**: PostgreSQL must be running before FastAPI service starts - requires proper Ansible task ordering and handlers
- **File Permissions**: SSL certificate group ownership (ssl-cert) and specific directory permissions need careful mapping to Ansible file modules

### Migration Order

1. **cache cookbook** (low risk, standalone caching services)
2. **nginx-multisite cookbook** (moderate complexity, security configurations)
3. **fastapi-tutorial cookbook** (high complexity, application deployment with database dependencies)

### Assumptions

- Current Chef cookbooks target Ubuntu/CentOS environments - Ansible playbooks will maintain same OS support
- Self-signed certificates are acceptable for development - production may require Let's Encrypt or CA-signed certificates
- Redis and PostgreSQL passwords can be migrated to Ansible Vault without changing actual credential values
- UFW firewall is the preferred firewall solution (vs iptables) for the target environment
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Vagrant development environment will be replaced with equivalent Ansible-based provisioning