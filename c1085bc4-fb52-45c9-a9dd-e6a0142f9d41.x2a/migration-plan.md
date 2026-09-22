# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban integration, UFW firewall rules, sysctl security tuning, SSH hardening, self-signed certificate generation

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication, custom Redis configuration patching, and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom configuration file manipulation, Memcached integration, Redis log directory setup

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (not examined but likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Shell script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - migrate to community.crypto collection for proper certificate lifecycle management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations in Ansible
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration patching**: The cache cookbook contains a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules with proper configuration management
- **Multi-cookbook coordination**: The nginx-multisite cookbook orchestrates multiple recipes (security, nginx, ssl, sites) that must be properly sequenced in Ansible playbooks
- **External cookbook dependencies**: Dependencies on community cookbooks (nginx, memcached, redisio) will need to be replaced with equivalent Ansible collections or custom roles
- **File resource management**: Static HTML files for different sites are managed through cookbook_file resources - migrate to ansible.builtin.copy or template modules
- **Service interdependencies**: PostgreSQL must be running before database creation, nginx must reload after configuration changes - ensure proper task ordering and handlers in Ansible

### Migration Order

1. **cache cookbook** (low risk, self-contained caching services with clear external dependencies)
2. **fastapi-tutorial cookbook** (moderate complexity, database setup and application deployment)
3. **nginx-multisite cookbook** (high complexity, multiple integrated security features and SSL management)

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- The Ruby-based Redis configuration patching is a workaround that can be replaced with proper template-based configuration management
- Database credentials and Redis passwords will be migrated to Ansible Vault for security
- The multi-site nginx configuration pattern will be preserved with the same domain structure (*.cluster.local)
- UFW and fail2ban security tools will remain the preferred security stack
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and compatible
- Vagrant-based development workflow will be maintained or replaced with equivalent local development tooling