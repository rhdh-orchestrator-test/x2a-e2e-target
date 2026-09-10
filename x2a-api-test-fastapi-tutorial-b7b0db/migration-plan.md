# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.template for configuration
- **External cookbook dependencies**: All external Chef Supermarket cookbooks need replacement with equivalent Ansible modules or custom tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider ansible.builtin.openssl_* modules for certificate lifecycle management
- **SSH hardening configurations**: Root login disable and password authentication disable via direct file manipulation - migrate to ansible.posix.sshd_config module
- **Firewall rules**: UFW commands executed directly - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail.local configuration - migrate to ansible.builtin.template with Ansible variables
- **Credential types identified**: Database passwords (2), Redis authentication (1), SSL certificate generation (3 sites)

### Technical Challenges

- **Ruby block configuration cleanup**: The Redis cookbook uses a ruby_block to manually edit configuration files - this complex logic needs translation to Ansible tasks using ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Multi-site SSL certificate generation**: Dynamic certificate generation for multiple sites requires Ansible loops and conditional logic based on site configuration
- **Service dependency management**: PostgreSQL must be running before database user creation - requires proper Ansible task ordering and handlers
- **Git repository synchronization**: FastAPI application deployment from GitHub requires ansible.builtin.git module with proper change detection
- **Python virtual environment management**: Complex pip installation within venv requires ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Python application with database dependencies but straightforward service patterns  
3. **nginx-multisite** (high complexity, multiple dependencies) - Complex multi-site configuration with SSL, security hardening, and firewall rules

### Assumptions

- Target systems will have Python 3 and pip available for FastAPI application deployment
- SSL certificates are acceptable as self-signed for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL service management follows standard systemd patterns on target systems
- UFW firewall is the preferred firewall solution (may need adaptation for RHEL/CentOS systems using firewalld)
- Git repository access to https://github.com/dibanez/fastapi_tutorial.git will remain available during migration
- Current Chef Solo execution model can be replaced with Ansible playbook execution without significant workflow changes
- Node attribute structure in solo.json can be directly mapped to Ansible variables with minimal restructuring
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated using native Ansible modules without feature loss