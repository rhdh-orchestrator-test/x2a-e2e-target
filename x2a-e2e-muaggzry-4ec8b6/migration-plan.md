# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and application deployment. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, UFW firewall rules, fail2ban jail configuration, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for testing cookbook functionality
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW configuration with specific port allowances (22, 80, 443) requires ufw Ansible module
- **Fail2ban configuration**: Custom jail.local template needs migration to Ansible template module
- **Credential patterns per module**:
  - cache: Redis requirepass in node attributes
  - fastapi-tutorial: PostgreSQL user password, database connection string in .env file
  - nginx-multisite: SSL certificate paths, no embedded credentials but certificate generation

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook uses ruby_block to patch Redis configuration files - needs conversion to Ansible lineinfile or replace modules
- **Service dependencies**: PostgreSQL must be running before database user creation - requires proper Ansible task ordering with handlers
- **Multi-site SSL generation**: Dynamic SSL certificate creation for multiple domains needs Ansible loops with openssl modules
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables
- **Package manager differences**: Cross-platform package installation (Ubuntu vs CentOS) needs conditional task execution in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web service)
2. **cache** (low complexity, independent caching layer)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- Current Chef cookbooks are actively used in production environments
- SSL certificates are currently self-signed for development/testing purposes
- Database passwords and Redis authentication are acceptable for migration to Ansible Vault
- UFW firewall rules are appropriate for target environments
- Systemd is available on target systems for service management
- Git repository access for FastAPI tutorial code will remain available
- PostgreSQL service management approach (system packages vs containers) is acceptable
- Current fail2ban and security configurations meet organizational requirements
- Multi-platform support (Ubuntu/CentOS) requirement will continue in Ansible implementation