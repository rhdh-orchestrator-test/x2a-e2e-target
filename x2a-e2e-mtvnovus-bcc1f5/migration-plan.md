# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (redis_secure_password_123), Memcached service, Redis log directory management, configuration file patching via Ruby block

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file with database credentials

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (requires review for Ansible conversion)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths configured but certificate provisioning not visible in reviewed files - requires investigation of certificate deployment strategy
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **System security**: Sysctl security parameters via template - migrate to ansible.posix.sysctl module
- **Fail2ban configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Database credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault and postgresql_* modules

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses a Ruby block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **External cookbook dependencies**: Three external Chef cookbooks need replacement with equivalent Ansible modules or custom role development
- **Multi-site nginx configuration**: Template-driven virtual host generation needs conversion to Ansible template module with proper Jinja2 templating
- **Git repository management**: FastAPI application deployment via git clone requires conversion to ansible.builtin.git module with proper change detection
- **Systemd service creation**: Custom systemd unit file creation needs migration to ansible.builtin.systemd module
- **PostgreSQL database initialization**: Database and user creation commands need conversion to community.postgresql modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web infrastructure)
2. **cache** (low-moderate complexity, independent caching services)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- SSL certificates are managed externally or through a separate process not visible in the reviewed cookbook files
- The Vagrant environment is used for development/testing and will need corresponding Ansible playbook for local development
- Database backup and maintenance procedures are handled outside of these cookbooks
- The Redis configuration patching via Ruby block indicates potential compatibility issues with the redisio cookbook that may require custom Ansible tasks
- Network configuration and DNS setup for the *.cluster.local domains is handled externally
- The FastAPI application's requirements.txt and application code structure are compatible with the current deployment method
- Log rotation and monitoring configurations are handled by external systems not covered in these cookbooks