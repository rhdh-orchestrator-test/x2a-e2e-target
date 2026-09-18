# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package for Redis installation and configuration

### Security Considerations

- **Hardcoded Credentials**: 
  - Redis password (`redis_secure_password_123`) in cache cookbook - migrate to Ansible Vault
  - PostgreSQL password (`fastapi_password`) in fastapi-tutorial cookbook - migrate to Ansible Vault
  - Database connection strings with embedded credentials - use Ansible Vault variables
- **SSL Certificate Management**: Self-signed certificate generation for development environments - implement with ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to ansible.builtin.template with fail2ban configuration
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives. This will need to be reimplemented using Ansible's ansible.builtin.lineinfile module with regex patterns or custom Jinja2 templates.
- **Multi-site SSL Certificate Generation**: The nginx-multisite cookbook dynamically generates SSL certificates for each configured site. This requires implementing a loop in Ansible with conditional certificate generation based on site configuration.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL being available. Ansible handlers and service ordering will need careful implementation to ensure proper startup sequence.
- **File Permissions and Ownership**: Complex permission schemes (ssl-cert group, specific directory modes) require careful mapping to Ansible's ansible.builtin.file module with proper user/group management.

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, Git operations, and service management

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- The PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the main branch will be stable
- UFW firewall is the preferred firewall solution (rather than iptables or firewalld)
- The ssl-cert group and directory permission scheme should be maintained for compatibility
- Systemd is available on target systems for service management
- The current Chef Solo execution model will be replaced with standard Ansible playbook execution
- Site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) represent the actual target hostnames and will not change during migration