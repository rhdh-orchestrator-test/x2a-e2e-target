# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL certificates, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-role-nginx or community.general.nginx modules
- **memcached (~> 6.0)**: Replace with ansible-memcached role or package/service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or davidwittman.redis role
- **Chef Supermarket cookbooks**: All external dependencies need Ansible Galaxy or custom role equivalents

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with certbot
- **SSH hardening**: Root login disabled, password authentication disabled - maintain in Ansible with lineinfile or sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Ansible with appropriate handlers
- **Sysctl security tuning**: Custom kernel parameters via template - use ansible.posix.sysctl module
- **File permissions**: SSL private keys with group ssl-cert access (mode 0710/0640) - maintain strict permissions in Ansible

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a ruby_block that manually edits Redis configuration files to remove problematic lines - this Chef-specific hack needs to be replaced with proper Ansible template management or lineinfile modules
- **Multi-site SSL automation**: The nginx-multisite cookbook dynamically generates SSL certificates for each configured site - requires Ansible loops and certificate management strategy
- **Service orchestration**: Complex service dependencies (PostgreSQL → database creation → application startup) need proper Ansible task ordering and handlers
- **Template variable mapping**: Chef ERB templates use node attributes that need to be mapped to Ansible variables and Jinja2 syntax
- **Package management**: Multi-platform support (Ubuntu/CentOS) requires Ansible conditionals or separate variable files for package names

### Migration Order

1. **cache cookbook** (low risk, isolated caching services, good starting point for learning Chef→Ansible patterns)
2. **nginx-multisite cookbook** (moderate complexity, establishes web infrastructure foundation for other services)
3. **fastapi-tutorial cookbook** (highest complexity due to application deployment, database setup, and service dependencies)

### Assumptions

- Current Chef Solo deployment model will be replaced with Ansible playbooks executed via ansible-playbook
- Vagrant development environment will be maintained with Ansible provisioner instead of shell scripts
- SSL certificates are currently self-signed for development - production deployment strategy for certificates is undefined
- Database credentials and Redis passwords are acceptable to be stored in Ansible Vault rather than external secret management
- The ruby_block hack in the Redis configuration suggests the redisio cookbook version has compatibility issues that may not exist in Ansible Redis roles
- Multi-platform support (Ubuntu/CentOS) is required to be maintained in the Ansible migration
- The current attribute-driven configuration model (solo.json) will be replaced with Ansible group_vars or host_vars
- Service restart/reload notifications in Chef will be replaced with Ansible handlers
- File and directory ownership/permissions must be preserved exactly as configured in Chef recipes