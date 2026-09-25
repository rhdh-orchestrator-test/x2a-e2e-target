# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with multi-site SSL configuration, security hardening via fail2ban/UFW, and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services infrastructure with memcached and Redis configuration including authentication and custom log directory setup
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (requirepass), custom Redis configuration cleanup via ruby_block, memcached service, Redis log directory management with proper ownership

**fastapi-tutorial**:
- Description: Python FastAPI application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service management, environment configuration file (.env) with database credentials

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package + service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Ansible tasks for Redis installation and configuration
- **Chef Solo execution model**: Replace with Ansible playbook execution targeting localhost or remote hosts

### Security Considerations

- **Hardcoded credentials in cache cookbook**: Redis password 'redis_secure_password_123' needs migration to Ansible Vault
- **PostgreSQL credentials in fastapi-tutorial**: Database password 'fastapi_password' requires Ansible Vault encryption
- **SSL certificate management**: nginx-multisite references SSL certificate paths (/etc/ssl/certs, /etc/ssl/private) - certificate deployment strategy needed
- **SSH security configurations**: Root login disabled, password authentication disabled - maintain these security postures in Ansible
- **Firewall rules**: UFW configuration for ports 22, 80, 443 - ensure proper firewall module usage
- **Fail2ban configuration**: Intrusion prevention settings need equivalent Ansible configuration

### Technical Challenges

- **Ruby block configuration cleanup**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - this needs conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Multi-site nginx configuration**: Complex template-driven virtual host configuration requires careful Ansible template conversion and loop handling for multiple sites
- **Service dependency orchestration**: FastAPI service depends on PostgreSQL being ready - implement proper Ansible handlers and service ordering
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure proper git module usage with appropriate revision handling
- **Python virtual environment management**: Complex pip installation within venv requires careful Ansible pip module configuration with virtualenv parameters

### Migration Order

1. **cache cookbook** (low risk, foundational service) - Redis and memcached are standalone services with minimal external dependencies
2. **nginx-multisite cookbook** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate availability
3. **fastapi-tutorial cookbook** (high complexity, multiple dependencies) - Requires PostgreSQL, Python environment, git repository, and systemd integration

### Assumptions

- SSL certificates for *.cluster.local domains are available or will be generated separately (Let's Encrypt, self-signed, or corporate CA)
- The target environment has internet access for git cloning from GitHub (https://github.com/dibanez/fastapi_tutorial.git)
- PostgreSQL installation and initial setup permissions are available on target systems
- The migration will maintain the same service architecture (nginx + FastAPI + Redis + memcached + PostgreSQL on single or multiple hosts)
- Current Chef Solo execution model suggests single-node deployment, but Ansible migration could support multi-node if needed
- The development Vagrant environment setup is not critical for production migration but may be useful for testing converted playbooks
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using Ansible modules rather than importing equivalent Ansible Galaxy roles
- The existing security configurations (fail2ban, UFW, SSH hardening) are requirements that must be maintained in the Ansible migration