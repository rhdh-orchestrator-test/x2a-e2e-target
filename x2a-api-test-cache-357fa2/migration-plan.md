# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and sysctl kernel parameter tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, custom nginx.conf with security headers

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (requirepass), custom log directory setup, configuration file post-processing via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with node attributes and run list orchestration
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and template-based configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo execution model**: Replace with Ansible playbook orchestration and inventory management

### Security Considerations

- **Hardcoded credentials in cache cookbook**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are embedded in recipe code - migrate to Ansible Vault
- **SSL certificate management**: Certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) need secure deployment strategy
- **SSH hardening configurations**: Root login disable and password authentication disable require careful migration to avoid lockout
- **Firewall rules**: UFW configuration with specific port allowances (22, 80, 443) needs systematic migration
- **Fail2ban jail configurations**: Custom jail.local template requires conversion to Ansible template with proper service restart handling
- **Sysctl security parameters**: Kernel parameter tuning via sysctl needs migration with proper validation

### Technical Challenges

- **Ruby block post-processing in Redis configuration**: The cache cookbook uses Ruby code to modify Redis config files after generation - this pattern needs conversion to Ansible lineinfile or replace modules
- **Chef resource notification chains**: Complex notification patterns between templates, services, and execute resources need careful mapping to Ansible handlers
- **Git repository management**: FastAPI cookbook clones from GitHub with revision tracking - requires ansible.builtin.git module with proper idempotency
- **Multi-site nginx configuration**: Dynamic site generation from attributes requires Ansible loops and template generation
- **PostgreSQL database initialization**: Database and user creation commands need conversion to community.postgresql modules with proper idempotency checks

### Migration Order

1. **cache** (moderate complexity, foundational service, clear external dependencies)
2. **nginx-multisite** (high complexity due to security configurations, but well-isolated functionality)
3. **fastapi-tutorial** (highest complexity due to application deployment, database setup, and service management)

### Assumptions

- SSL certificates are manually managed and placed in standard system locations (/etc/ssl/certs, /etc/ssl/private)
- The GitHub repository for FastAPI tutorial (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- PostgreSQL service is expected to be managed by the system package manager and not require custom compilation
- The target environment has internet access for package installation and git repository cloning
- UFW firewall rules are acceptable for the target environment and won't conflict with existing security policies
- The Redis configuration modifications performed by Ruby blocks are still necessary in the target environment
- Systemd is the target service manager (inferred from fastapi-tutorial systemd service creation)
- The 'www-data' user and group exist on target systems for nginx file ownership
- Development and production environments will use the same cookbook configurations with attribute overrides