# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment variable management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, security headers, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) - requires Ansible Galaxy equivalent mapping
- `solo.json`: Chef Solo configuration with run list and node attributes - needs conversion to Ansible inventory and group_vars
- `solo.rb`: Chef Solo configuration file - replaced by ansible.cfg
- `Vagrantfile`: Development environment provisioning - can be adapted for Ansible provisioner
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to preserve

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support required based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **fail2ban**: Use ansible.builtin.package and template modules for jail configuration
- **ufw**: Replace with community.general.ufw module

### Security Considerations

- **Hardcoded credentials**: Redis password and PostgreSQL credentials are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Certificate paths are configured but certificate provisioning method unclear - needs SSL automation strategy
- **SSH hardening**: Root login disable and password authentication disable - preserve with ansible.builtin.lineinfile
- **Firewall rules**: UFW configuration with specific port allowances - migrate to community.general.ufw tasks
- **System security**: sysctl security parameters via template - preserve with ansible.posix.sysctl module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Jinja2 format

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis config files post-installation - requires custom Ansible task or improved template approach
- **Multi-platform support**: Cookbooks support both Ubuntu and CentOS - ensure Ansible playbooks handle package name differences and service variations
- **Database initialization**: PostgreSQL user and database creation uses shell commands - migrate to community.postgresql.* modules for idempotency
- **Git repository management**: FastAPI app deployment clones from GitHub - use ansible.builtin.git module with proper change detection
- **Service dependencies**: Complex service startup order (PostgreSQL before FastAPI, nginx after SSL setup) - use proper task dependencies and handlers

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached are independent services with clear configuration
2. **nginx-multisite** (moderate complexity) - Web server with security features but no application dependencies  
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service integration

### Assumptions

- SSL certificates are manually managed or provided externally (no automated certificate provisioning found in cookbooks)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef external cookbook versions are compatible with target system package versions
- UFW firewall rules are appropriate for the target environment (no custom port requirements beyond HTTP/HTTPS/SSH)
- Redis password authentication is required in production (hardcoded password suggests development/testing environment)
- PostgreSQL runs locally on the same server as the FastAPI application (no remote database configuration found)
- The nginx sites use self-signed or manually installed certificates (no Let's Encrypt or automated CA integration detected)
- System security hardening requirements remain the same (SSH restrictions, sysctl parameters, fail2ban rules)
- The Ruby block hack for Redis configuration indicates potential compatibility issues with the redisio cookbook version that may not exist with direct Ansible Redis management