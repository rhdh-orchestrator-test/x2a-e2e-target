# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes Redis log directory setup and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local development environment)

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations
- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Database credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault with community.postgresql modules

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or template modules
- **Multi-site SSL certificate generation**: Dynamic certificate generation per site requires Ansible loops with community.crypto modules
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - use Ansible handlers and service dependencies
- **Git repository synchronization**: Chef git resource behavior needs replication with ansible.builtin.git module
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables

### Migration Order
1. **cache** (low risk, standalone caching services)
2. **nginx-multisite** (moderate complexity, security and SSL configuration)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions
- Target systems will maintain the same OS versions (Ubuntu 18.04+, CentOS 7+) as specified in Chef metadata
- SSL certificates can remain self-signed for development environments, or migration team will provide CA-signed certificate deployment process
- PostgreSQL and Redis passwords will be migrated to Ansible Vault rather than remaining hardcoded
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- UFW firewall rules are appropriate for the target environment and no additional ports need to be opened
- The ruby_block Redis configuration patching can be replaced with standard Ansible configuration management without breaking Redis functionality
- Systemd is available on target systems for service management
- The nginx sites configuration structure (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved in the Ansible implementation