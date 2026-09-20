# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and application deployment. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers with moderate Chef/Ansible experience.

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
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with cookbook run_list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - likely contains Chef Solo execution commands

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: Self-signed certificate generation via OpenSSL commands - migrate to community.crypto.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable via sed commands - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules management via shell commands - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby code for Redis configuration file manipulation that will need conversion to Ansible file manipulation tasks or Jinja2 templating
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple domains requires loop-based Ansible task structure with proper certificate validation
- **Service Dependencies**: PostgreSQL database creation and user provisioning timing dependencies need careful Ansible task ordering with proper wait conditions
- **Template Migration**: ERB templates (nginx.conf.erb, security.conf.erb, site.conf.erb) need conversion to Jinja2 with variable mapping
- **File Resource Management**: Chef's cookbook_file resources for static HTML files need migration to ansible.builtin.copy tasks with proper source file organization

### Migration Order

1. **cache** (Priority 1: Low complexity, standalone caching services)
2. **nginx-multisite** (Priority 2: Moderate complexity, security configurations, template migration)
3. **fastapi-tutorial** (Priority 3: High complexity, application deployment, database dependencies)

### Assumptions

- Target environments will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis service management approaches will remain similar between Chef and Ansible
- The ruby_block configuration patching in the cache cookbook represents a workaround that may not be needed with proper Ansible Redis module usage
- Vagrant development workflow will be maintained with ansible_local provisioner
- Static HTML files in cookbook files/ directories represent placeholder content that will be managed similarly in Ansible
- UFW firewall is the preferred firewall solution (vs. iptables direct management)
- Fail2ban configuration requirements will remain consistent with current jail.local template settings
- SSH hardening requirements (root disable, password auth disable) are security mandates that must be preserved
- The FastAPI application deployment pattern (git clone, venv, systemd service) represents the preferred application deployment approach