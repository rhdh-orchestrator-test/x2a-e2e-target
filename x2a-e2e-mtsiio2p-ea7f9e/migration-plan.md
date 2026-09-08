# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, Redis configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate auto-generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Local development environment setup
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security settings
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban integration**: SSH and nginx protection - migrate to community.general.fail2ban module
- **Sysctl security parameters**: Kernel security hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block configuration patching**: The Redis cookbook uses a ruby_block to modify configuration files post-installation - replace with Ansible lineinfile or template modules
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires loop-based certificate generation in Ansible
- **Database initialization**: PostgreSQL user and database creation with proper privilege assignment needs careful migration to postgresql_* modules
- **Service dependencies**: Ensure proper service ordering (PostgreSQL before FastAPI, nginx after SSL certificates)
- **Template migration**: Convert ERB templates to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations

### Migration Order

1. **cache cookbook** (low risk, standalone caching services)
2. **nginx-multisite cookbook** (moderate complexity, security configurations but no external dependencies)
3. **fastapi-tutorial cookbook** (high complexity, database dependencies and application deployment)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development; production deployment will require proper CA-signed certificates or Let's Encrypt integration
- Current hardcoded passwords are development-only and will be replaced with proper secret management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- PostgreSQL service management approach (sudo -u postgres psql commands) is acceptable or can be replaced with Ansible postgresql modules
- UFW firewall is the preferred firewall solution for the target environment
- Systemd is available on target systems for service management
- The multi-site configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved in the Ansible implementation