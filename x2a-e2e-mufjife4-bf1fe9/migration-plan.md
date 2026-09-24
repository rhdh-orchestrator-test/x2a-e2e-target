# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching, and application deployment. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database integration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node configuration - contains run list and attribute overrides for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
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
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Management**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **SSL Certificate Management**: Self-signed certificate generation per site - migrate to community.crypto.openssl_* modules
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial (PostgreSQL password: 'fastapi_password')
  - SSL certificate generation uses hardcoded subject information
  - No encrypted data bags or Chef Vault usage detected
  - Credentials stored in plain text attributes and templates (3 modules affected)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need custom Ansible lineinfile tasks or template management
- **Multi-site SSL Certificate Generation**: Each nginx site requires individual SSL certificate generation with site-specific filenames and paths - requires dynamic task generation in Ansible
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment needs careful migration to ansible.builtin.postgresql_* modules
- **Service Dependencies**: FastAPI service depends on PostgreSQL being available - requires proper task ordering and handlers in Ansible
- **Template Variable Mapping**: Chef ERB templates use node attributes that need mapping to Ansible variables (nginx.conf.erb, site.conf.erb, security configurations)

### Migration Order

1. **cache** (low risk, high value) - Simple service installation and configuration, good starting point
2. **nginx-multisite** (moderate complexity) - Core web infrastructure, security hardening, SSL management
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database dependencies and service management

### Assumptions

- Target environment will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis passwords can be externalized to Ansible Vault during migration
- Current UFW firewall rules are sufficient and don't require additional ports
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available
- Chef Supermarket dependencies (nginx, memcached, redisio cookbooks) functionality can be replicated with native Ansible modules
- Development workflow using Vagrant can be replaced with ansible-playbook execution
- No Chef Server integration exists (solo.rb indicates Chef Solo usage)
- File permissions and ownership requirements match between Chef and Ansible execution contexts