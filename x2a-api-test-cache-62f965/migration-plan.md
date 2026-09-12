# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL termination, security hardening (fail2ban, UFW firewall), and multi-site hosting for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificates, fail2ban protection, UFW firewall rules, SSH hardening, sysctl security tuning, multiple virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local)

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and Python virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH security configuration**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall rules**: UFW configuration for HTTP/HTTPS/SSH - migrate using community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate using ansible.builtin.template module
- **Database credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault for credential management

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a ruby_block that manually patches Redis configuration files - this will need to be reimplemented using Ansible's lineinfile or replace modules with proper regex patterns
- **Complex template dependencies**: Multiple ERB templates with cross-references between nginx configuration, security settings, and site definitions - requires careful variable mapping in Ansible
- **Service orchestration**: Dependencies between PostgreSQL, Redis, memcached, and nginx services need proper handler ordering in Ansible playbooks
- **Git repository management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but isolated functionality  
3. **nginx-multisite** (high complexity, security dependencies) - Complex nginx configuration with security hardening, SSL, and firewall rules that affect system-wide security

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (development/testing setup)
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of required virtual hosts
- PostgreSQL and Redis password security can be improved through Ansible Vault without changing the application connection strings
- The ruby_block Redis configuration fixes in the cache cookbook address specific version compatibility issues that may not be needed with newer Redis versions
- Vagrant-based development workflow will be maintained or replaced with equivalent local development tooling
- The current Chef Solo approach indicates a single-node deployment model that will be preserved in the Ansible migration