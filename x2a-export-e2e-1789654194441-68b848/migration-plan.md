# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with cookbook run_list and node attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in nginx configuration need secure deployment mechanism
- **SSH hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW firewall configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban integration**: Jail configuration for nginx protection needs template migration
- **Sysctl security tuning**: Kernel parameter hardening configurations require careful validation

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook uses ruby_block to patch Redis configuration files - this custom logic needs reimplementation in Ansible using lineinfile or template modules
- **Service dependencies**: Complex service startup ordering (PostgreSQL before FastAPI, nginx after SSL setup) requires careful Ansible handler and dependency management
- **Multi-site nginx configuration**: Dynamic site generation based on node attributes needs conversion to Ansible loops and templates
- **Git repository management**: FastAPI cookbook clones and manages git repositories - requires ansible.builtin.git module with proper change detection
- **Virtual environment management**: Python venv creation and pip dependency installation needs ansible.builtin.pip module configuration

### Migration Order

1. **cache** (moderate complexity, standalone service)
2. **nginx-multisite** (high complexity due to security integrations, but foundational)
3. **fastapi-tutorial** (depends on nginx for reverse proxy, complex application deployment)

### Assumptions

- SSL certificates are manually managed or obtained via external process (no Let's Encrypt automation detected)
- The "cluster.local" domain names suggest internal/development environment usage
- PostgreSQL installation assumes default package repository versions are acceptable
- Redis configuration patching via ruby_block suggests upstream cookbook limitations that may not apply to Ansible redis modules
- UFW firewall rules assume no existing iptables conflicts
- SSH service restart during hardening assumes no active SSH sessions will be disrupted
- Python 3 and pip availability from default package repositories
- Git repository access does not require authentication (public repository)
- Systemd is the target init system for service management
- The FastAPI application runs as root user (security consideration for future improvement)