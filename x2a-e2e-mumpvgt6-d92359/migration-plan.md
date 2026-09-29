# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, including custom Redis configuration fixes and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, memcached integration, custom Redis config patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening (fail2ban, UFW firewall), and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains custom Ruby code for Redis configuration patching - requires translation to Ansible lineinfile or template modules
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple domains needs careful templating in Ansible
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - use Ansible handlers and service dependencies
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) require proper Ansible file module configuration
- **Git Repository Management**: FastAPI cookbook clones from GitHub - ensure proper git module configuration with revision tracking

### Migration Order

1. **nginx-multisite** (foundational infrastructure, security hardening)
2. **cache** (supporting services, moderate complexity with Ruby block translation)
3. **fastapi-tutorial** (application layer, depends on database and potentially cache services)

### Assumptions

- Current Chef cookbooks are actively used in production environments
- SSL certificates are currently self-signed for development/testing purposes
- PostgreSQL and Redis services are intended to run on the same hosts as the web applications
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- UFW firewall rules are appropriate for the target environment's security requirements
- The 'ssl-cert' group management approach is suitable for the target operating systems
- Chef Solo configuration in solo.json represents the desired final state for all managed nodes
- External cookbook dependencies (nginx, memcached, redisio) can be replaced with equivalent Ansible modules without functionality loss
- The custom Redis configuration patching in the ruby_block is still necessary in the target environment
- Systemd is the target service manager for all managed services