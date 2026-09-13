# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

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
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - maintain with ansible.posix.sysctl and lineinfile modules
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Custom jail configuration for nginx protection - use community.general.fail2ban module
- **Credential types per module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no stored credentials

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires Ansible loops and conditional logic based on site configuration
- **Service dependency management**: PostgreSQL must be running before database user creation - requires proper task ordering and handlers
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables
- **Git repository management**: FastAPI tutorial cloning requires idempotent git operations with proper revision handling

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web server)
2. **cache** (low complexity, independent caching services)  
3. **fastapi-tutorial** (high complexity, database dependencies and application deployment)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development; production may require CA-signed or Let's Encrypt certificates
- Current hardcoded passwords are development placeholders and will be replaced with proper secret management
- PostgreSQL and Redis services can be managed via standard Ansible modules without custom compilation
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- UFW firewall rules and fail2ban configurations are suitable for the target environment security requirements
- Systemd is available on target systems for service management (implied by Ubuntu 18.04+ and CentOS 7+ support)