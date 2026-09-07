# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379 with authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication (requirepass), memcached integration, Redis log directory management, configuration file post-processing

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with attribute overrides for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox (development), production platform not specified
- **Cloud Platform**: Not specified - appears to be platform-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - maintain firewall state management
- **Fail2ban Integration**: Jail configuration for nginx protection - ensure fail2ban rules are properly migrated
- **Credential Patterns per Module**:
  - cache: Redis requirepass password (hardcoded)
  - fastapi-tutorial: PostgreSQL user password, database connection string (hardcoded in .env file)
  - nginx-multisite: SSL certificate generation (self-signed, no sensitive data stored)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook uses a Ruby block to manually edit Redis config files post-installation - this will need to be replaced with proper template management in Ansible
- **Multi-site SSL Certificate Generation**: Each nginx site gets its own self-signed certificate - need to implement certificate generation loop in Ansible
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - ensure proper service ordering in Ansible playbooks
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need careful handling in Ansible
- **Template Migration**: Multiple ERB templates need conversion to Jinja2 format

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached have minimal dependencies
2. **nginx-multisite** (moderate complexity) - Security hardening and SSL setup, but well-contained
3. **fastapi-tutorial** (high complexity) - Database setup, application deployment, and service dependencies

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt integration required initially)
- PostgreSQL and Redis will continue to run on the same hosts as the applications
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- Current hardcoded passwords are acceptable for migration (will be moved to Ansible Vault)
- UFW firewall is the preferred firewall solution for the target environment
- Systemd is available on target systems for service management
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the production requirements
- No external load balancer or reverse proxy exists upstream of nginx
- The current Chef Solo deployment model will be replaced with standard Ansible playbook execution