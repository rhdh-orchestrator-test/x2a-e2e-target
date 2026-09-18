# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-role-nginx or community.general.nginx modules
- **memcached (~> 6.0)**: Replace with community.general.memcached or custom Ansible tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis or geerlingguy.redis role
- **Chef ruby_block constructs**: Convert custom Ruby logic to Ansible lineinfile/replace modules or custom scripts

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs conversion to Ansible crypto modules
- **SSH hardening**: Root login disable and password authentication disable configurations
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban integration**: Jail configuration for intrusion prevention
- **Credential patterns per module**:
  - cache: Redis authentication password (1 hardcoded credential)
  - fastapi-tutorial: PostgreSQL database credentials (2 hardcoded credentials)
  - nginx-multisite: SSL certificate generation (certificate management, no stored credentials)

### Technical Challenges

- **Ruby block logic conversion**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible file manipulation modules
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure Ansible git module handles the same repository and branch logic
- **Service dependency ordering**: PostgreSQL must be running before database user creation - maintain proper task ordering in Ansible
- **Multi-site SSL automation**: Self-signed certificate generation for multiple domains needs conversion to Ansible crypto collection
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with proper variable scoping

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web server)
2. **cache** (low-moderate complexity, independent caching layer)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- Current Chef cookbooks are working and tested in the target environment
- External cookbook dependencies (nginx, memcached, redisio) are compatible with the versions specified in Berksfile
- SSL certificates are only needed for development/testing (self-signed generation approach)
- PostgreSQL service management and database creation permissions are available on target systems
- UFW firewall is the preferred firewall solution (vs iptables or firewalld)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Target systems have internet access for package installation and git repository cloning
- The ruby_block configuration fixes in the cache cookbook are still necessary for the Redis version that will be installed via Ansible
- Systemd is the service manager on target systems (for FastAPI service management)
- The current site configuration in solo.json represents the desired final state for nginx virtual hosts