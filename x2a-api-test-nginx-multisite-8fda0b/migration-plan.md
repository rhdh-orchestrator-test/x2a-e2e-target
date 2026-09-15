# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificate paths configured but certificate provisioning not automated - implement proper certificate management
- **SSH Hardening**: Root login disable and password authentication disable via sed commands - replace with ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via execute resources - replace with community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate to community.general.fail2ban module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - will require custom Ansible tasks with lineinfile or replace modules
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering with handlers and wait_for conditions
- **Multi-site Nginx Configuration**: Dynamic site generation from attributes requires Jinja2 templating and loop constructs
- **Git Repository Management**: FastAPI cookbook clones and manages git repositories - replace with ansible.builtin.git module with proper idempotency

### Migration Order

1. **cache** (moderate complexity, no dependencies on other cookbooks)
2. **fastapi-tutorial** (moderate complexity, standalone application)
3. **nginx-multisite** (high complexity, security configurations, multiple templates)

### Assumptions

- SSL certificates will be provided externally or managed through Let's Encrypt integration (not currently automated in Chef cookbooks)
- PostgreSQL installation and initial configuration is handled by system packages rather than dedicated database cookbooks
- The target environment will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Current hardcoded passwords are acceptable for development but will be moved to Ansible Vault for production
- The multi-site nginx configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
- UFW firewall rules are sufficient and no additional iptables complexity is required
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Redis configuration patching via ruby_block indicates potential version compatibility issues that may need addressing in the Ansible version