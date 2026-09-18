# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning (likely contains VM configuration)
- `vagrant-provision.sh`: Shell script for Vagrant provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant-based development environment (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or custom Ansible tasks for memcached installation and configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom Redis configuration templates

### Security Considerations

- **Hardcoded credentials**: Redis password (`redis_secure_password_123`) and PostgreSQL credentials (`fastapi_password`) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules or integration with Let's Encrypt via community.crypto collection
- **SSH hardening**: Root login disable and password authentication disable configurations need migration to ansible.posix.sshd_config or lineinfile modules
- **Firewall rules**: UFW configuration needs migration to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration needs migration to ansible.builtin.template with fail2ban service management
- **Credential types identified**: Database passwords (PostgreSQL, Redis), SSL certificate paths, SSH configuration parameters

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a ruby_block that manually patches Redis configuration files - this needs to be replaced with proper Ansible template management or lineinfile modules
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready, requiring proper Ansible handler ordering and dependency management
- **Multi-site SSL automation**: Self-signed certificate generation for multiple sites needs loop-based Ansible tasks with proper certificate validation
- **External cookbook dependencies**: Three external Chef cookbooks need to be replaced with equivalent Ansible roles or custom implementations

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **fastapi-tutorial** (moderate complexity, database dependencies but well-contained)
3. **nginx-multisite** (high complexity, multiple security integrations and SSL management)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require Let's Encrypt or CA-signed certificates)
- The Vagrant development environment will be replaced with an equivalent Ansible-based development setup
- Database credentials and Redis passwords will be migrated to Ansible Vault for security
- The current Chef Solo execution model will be replaced with Ansible playbook execution
- UFW firewall and fail2ban are the preferred security tools for the target environment
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and unchanged
- System service management will continue using systemd on the target platforms
- The nginx sites configuration structure (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved in the Ansible implementation