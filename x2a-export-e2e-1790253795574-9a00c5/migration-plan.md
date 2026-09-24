# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment variable management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx, memcached, redisio) and local cookbook paths
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or custom Ansible tasks for memcached installation and configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom Redis configuration templates

### Security Considerations

- **Hardcoded credentials**: Redis password and PostgreSQL credentials are embedded in recipe files - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH hardening**: SSH configuration changes need careful migration to avoid lockouts during deployment
- **Firewall rules**: UFW commands need conversion to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration requires Ansible template migration
- **Credential patterns per module**:
  - cache: Redis password in plain text
  - fastapi-tutorial: PostgreSQL credentials in plain text, database connection string in environment file
  - nginx-multisite: SSL certificate paths and security configurations

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to modify Redis config files post-installation - this needs conversion to Ansible lineinfile or template modules
- **Multi-site SSL automation**: Complex logic for generating certificates per site needs careful Ansible loop implementation
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible handler and dependency management
- **External cookbook dependencies**: Three external Chef cookbooks need equivalent Ansible roles or custom implementations

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational infrastructure)
2. **cache** (low-moderate complexity, independent services)
3. **fastapi-tutorial** (moderate complexity, depends on database setup)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are development-only and will be replaced with Ansible Vault in production
- The Ruby-based Redis configuration patching indicates potential issues with the redisio cookbook that may not exist in Ansible Redis roles
- Vagrant development workflow will be maintained or replaced with equivalent Ansible-based local development
- The solo.json attribute overrides suggest environment-specific configurations that will need Ansible inventory group_vars or host_vars structure
- UFW firewall rules are appropriate for the target environment (may need iptables or firewalld alternatives)
- Systemd is available on target systems for service management (cookbook creates systemd unit files)