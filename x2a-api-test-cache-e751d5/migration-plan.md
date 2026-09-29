# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban intrusion prevention, UFW firewall rules, sysctl security tuning, SSH hardening, self-signed certificate generation

**cache**:
- Description: Caching services layer providing both Redis (with authentication) and Memcached instances, includes Redis configuration workarounds and custom log directory setup
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, Redis log directory management, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, includes Git-based source deployment, Python virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attribute overrides for nginx domains and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant-based development environment (VirtualBox/VMware implied)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH hardening**: Root login disable and password authentication disable require careful migration to maintain access
- **Firewall rules**: UFW configuration needs migration to community.general.ufw module
- **Fail2ban configuration**: Template-based jail.local configuration requires Ansible template migration
- **File permissions**: SSL private key permissions (640, ssl-cert group) need careful preservation

### Technical Challenges

- **Ruby block workarounds**: The Redis configuration patching via ruby_block in cache cookbook requires custom Ansible solution using lineinfile or replace modules
- **Multi-site SSL automation**: Complex nginx site configuration with SSL certificate generation needs careful Ansible playbook structure
- **Service dependencies**: PostgreSQL must be running before FastAPI application deployment - requires proper task ordering and handlers
- **Git repository management**: FastAPI source deployment from Git requires idempotent Ansible git module usage
- **Python virtual environment**: Complex pip dependency installation in venv requires ansible.builtin.pip with virtualenv parameters

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires cache and nginx services

### Assumptions

- Current Chef cookbooks target Ubuntu/CentOS environments - Ansible playbooks will maintain same OS support
- Self-signed certificates are acceptable for development - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL database content migration is not required - only fresh database/user creation
- Vagrant development environment will be replaced with equivalent Ansible-based local testing
- Network connectivity allows Git repository access for FastAPI source deployment
- Target systems have internet access for package installation and pip dependencies
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- UFW firewall rules are appropriate for target environment security requirements
- Redis configuration workarounds in ruby_block are still necessary and will be replicated in Ansible