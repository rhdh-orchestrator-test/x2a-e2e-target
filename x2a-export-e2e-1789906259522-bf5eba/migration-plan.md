# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes Redis log directory setup and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening with fail2ban and UFW firewall, SSH configuration lockdown
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH security configuration**: Root login disabled, password authentication disabled - maintain these security practices in Ansible
- **Firewall rules**: UFW configuration for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom security parameters - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration patching**: Complex ruby_block that modifies Redis config file post-installation requires careful translation to Ansible lineinfile or template tasks
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site needs loop-based Ansible tasks with proper certificate validation
- **PostgreSQL database initialization**: SQL commands executed via shell need migration to community.postgresql.* modules for idempotency
- **Service dependencies**: Proper service ordering (PostgreSQL before FastAPI, nginx after SSL setup) requires careful task dependencies
- **Template migration**: ERB templates need conversion to Jinja2 format with equivalent variable substitution

### Migration Order

1. **cache cookbook** (low risk, standalone service)
   - Memcached installation and configuration
   - Redis installation with authentication
   - Service management and log directory setup

2. **nginx-multisite cookbook** (moderate complexity, security-critical)
   - Security hardening (fail2ban, UFW, SSH)
   - SSL certificate generation
   - Nginx configuration and multi-site setup

3. **fastapi-tutorial cookbook** (high complexity, application dependencies)
   - PostgreSQL database setup
   - Python application deployment
   - Service integration and startup dependencies

### Assumptions

- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require proper CA certificates)
- Redis and PostgreSQL passwords can be migrated to Ansible Vault without changing the actual credential values
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Site-specific static files (index.html for test, ci, status sites) will be maintained in the same structure
- UFW firewall rules and fail2ban configuration requirements remain the same for the target environment
- The complex Redis configuration patching in the cache cookbook addresses specific compatibility issues that may still be relevant
- Systemd service management approach will be maintained for the FastAPI application
- Document root paths may need adjustment between solo.json configuration (/var/www/) and cookbook attributes (/opt/server/)