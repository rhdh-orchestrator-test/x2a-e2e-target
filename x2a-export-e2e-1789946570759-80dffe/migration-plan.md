# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, includes Redis log directory management and configuration file patching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication (redis_secure_password_123), custom Redis configuration patching, Memcached integration, log directory creation

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), self-signed certificate generation, fail2ban integration, UFW firewall configuration, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations
- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban integration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Database credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault with community.postgresql.* modules

### Technical Challenges
- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually patches Redis configuration files by removing specific lines - this will require custom Ansible tasks with lineinfile or template modules
- **Multi-site nginx configuration**: Dynamic site generation based on attributes requires Ansible loops and template generation for each virtual host
- **Service dependencies**: FastAPI service depends on PostgreSQL being ready - will need proper task ordering and handlers in Ansible
- **File permissions and ownership**: Complex SSL certificate permissions (ssl-cert group) need careful mapping to Ansible file module parameters
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure Ansible git module handles repository updates properly

### Migration Order
1. **cache cookbook** (low risk, isolated caching services)
2. **fastapi-tutorial cookbook** (moderate complexity, database dependencies)
3. **nginx-multisite cookbook** (high complexity, security configurations, SSL management)

### Assumptions
- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using equivalent Ansible modules rather than direct cookbook translations
- The current Vagrant-based development workflow will be replaced with Ansible playbook execution
- SSL certificate management will transition from self-signed certificates to a more robust certificate management approach
- Database credentials and Redis passwords will be externalized to Ansible Vault rather than remaining hardcoded
- The multi-site nginx configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained in the Ansible implementation
- UFW and fail2ban security configurations are requirements that must be preserved in the migration
- The FastAPI application deployment pattern (git clone, virtual environment, systemd service) represents the desired deployment methodology for the target environment