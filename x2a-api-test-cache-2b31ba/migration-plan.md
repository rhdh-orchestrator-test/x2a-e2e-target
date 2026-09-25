# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application with comprehensive security hardening. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl kernel parameter tuning

**cache**:
- Description: Dual caching service configuration with memcached and Redis, including Redis authentication and custom configuration patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
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
- **memcached (~> 6.0)**: Replace with community.general.memcached or direct package installation and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes need secure deployment mechanism via Ansible Vault or external certificate management
- **SSH security hardening**: Root login disable and password authentication disable configurations need careful migration to ensure access is maintained
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) requires precise Ansible firewall module usage
- **System security**: Sysctl kernel parameter tuning and fail2ban configuration need validation in target environment
- **Database credentials**: PostgreSQL user creation with embedded passwords requires Ansible Vault integration

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a ruby_block that manually edits Redis configuration files to remove problematic lines - this Chef-specific workaround needs to be replaced with proper Ansible template management or lineinfile modules
- **Multi-site nginx configuration**: The nginx-multisite cookbook uses Chef attributes and loops to create multiple SSL-enabled virtual hosts - requires Ansible template loops and variable structures
- **Git repository management**: FastAPI application deployment via git clone needs Ansible git module with proper change detection and service restart coordination
- **Service dependency chains**: Complex notification chains between template changes and service restarts need careful Ansible handler design
- **Cross-cookbook dependencies**: The nginx-multisite default recipe includes multiple sub-recipes that need to be orchestrated properly in Ansible playbook task ordering

### Migration Order

1. **cache** (low risk, standalone service) - Independent caching services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but isolated from web tier
3. **nginx-multisite** (high complexity, security-critical) - Web server with security hardening that depends on proper SSL and firewall configuration

### Assumptions

- SSL certificates for *.cluster.local domains are available and will be managed outside of this automation or via separate certificate management playbooks
- PostgreSQL installation and initial setup is acceptable to be managed by Ansible rather than external database provisioning
- The target environment has internet access for git repository cloning and package installation
- The ruby_block workaround in the Redis configuration indicates potential compatibility issues with the redisio cookbook version that may not exist in direct Redis package management
- UFW firewall rules are appropriate for the target environment and won't conflict with existing network security policies
- The Chef Solo configuration suggests single-node deployment rather than multi-node orchestration
- Development and production environments will use the same Vagrant-based approach or the Vagrantfile is development-only
- The hardcoded passwords in the current configuration are acceptable for development but will need proper secret management for production deployment