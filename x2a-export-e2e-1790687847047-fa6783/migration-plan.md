# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and application deployment. The migration involves 3 cookbooks with moderate complexity, including security hardening, SSL configuration, and database integration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, custom nginx configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password (`redis_secure_password_123`) and PostgreSQL credentials (`fastapi_password`) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL paths and certificate deployment need secure handling in Ansible
- **SSH hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) requires ufw module or firewalld equivalent
- **Fail2ban configuration**: Custom jail.local template needs migration to Ansible template module
- **Sysctl security tuning**: Security kernel parameters require sysctl module migration

### Technical Challenges

- **Custom Redis configuration patching**: The cache cookbook uses a Ruby block to modify Redis config files post-installation - this needs conversion to Ansible lineinfile or replace modules
- **Multi-site nginx configuration**: Dynamic site creation based on node attributes requires Ansible loops and conditional logic
- **PostgreSQL database initialization**: Database and user creation commands need migration to postgresql_db and postgresql_user modules
- **Systemd service management**: Custom service file creation and daemon-reload handling requires systemd module usage
- **Git repository cloning with dependency installation**: FastAPI app deployment combines git clone with pip install in virtual environment - needs ansible.builtin.git and pip modules

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to security integration and multi-site configuration)
3. **fastapi-tutorial** (moderate complexity, depends on database setup and application deployment patterns)

### Assumptions

- SSL certificates are manually managed or obtained through external processes (no automated certificate generation visible in current cookbooks)
- The Redis configuration patching hack suggests potential compatibility issues that may need investigation in target environment
- Database credentials are acceptable to be stored in Ansible Vault rather than external secret management system
- UFW firewall is preferred over iptables/firewalld (Ubuntu-centric approach may need adjustment for RHEL targets)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo deployment model can be replaced with Ansible playbook execution model
- No Chef Server integration exists that would require additional migration considerations
- The Vagrant development environment pattern should be preserved in the Ansible version