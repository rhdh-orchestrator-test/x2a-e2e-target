# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **SSH Hardening**: Migration of SSH configuration changes (PermitRootLogin no, PasswordAuthentication no) to ansible.posix.sshd_config module
- **Firewall Management**: UFW rules migration to community.general.ufw module with proper rule ordering
- **SSL Certificate Management**: Self-signed certificate generation using community.crypto.openssl_* modules
- **Fail2ban Configuration**: Template-based jail.local configuration migration to ansible.builtin.template
- **Sysctl Security Tuning**: Security parameter configuration via ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials identified in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate paths and configurations in nginx-multisite attributes
  - Environment variables in FastAPI .env file containing database connection strings

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - this will need to be replaced with ansible.builtin.lineinfile or ansible.builtin.replace tasks
- **Dynamic Site Generation**: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes - requires Ansible template loops and conditional logic
- **Service Dependencies**: PostgreSQL must be running before FastAPI application setup - requires proper task ordering and handlers
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need careful mapping to Ansible file module parameters

### Migration Order

1. **cache** (low risk, standalone service)
2. **nginx-multisite** (moderate complexity, security configurations)
3. **fastapi-tutorial** (high complexity, database dependencies, application deployment)

### Assumptions

- Target systems will have Python 3 available for Ansible execution
- SSL certificates are self-signed for development (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL installation method may vary between distributions (package names, service management)
- Redis configuration file location may differ across OS versions (/etc/redis/ vs /etc/redis.conf)
- UFW is the preferred firewall solution (may need iptables alternative for RHEL-based systems)
- Git repository access for FastAPI tutorial clone assumes public repository or SSH key availability
- Systemd is available on target systems for service management
- The ruby_block configuration fixes in the cache cookbook suggest Redis package configuration issues that may not exist with different package versions