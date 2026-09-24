# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

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
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment focused

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - maintain with ansible.posix.sysctl and lineinfile modules
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Jail configuration via templates - use community.general.fail2ban module
- **Database credentials**: PostgreSQL user creation with embedded passwords - migrate to ansible.builtin.postgresql_* modules with vault integration

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or template modules with proper conditionals
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure idempotency with ansible.builtin.git module and proper change detection
- **Multi-site SSL automation**: Dynamic certificate generation per site requires loop-based certificate creation in Ansible
- **Service dependency management**: PostgreSQL must be running before database operations - use proper handler chains and service dependencies
- **Template variable scoping**: Chef node attributes need conversion to Ansible host_vars/group_vars structure

### Migration Order

1. **cache** (low risk, standalone service) - Start with Redis/Memcached as they have minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Core infrastructure component with security features but well-defined scope
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- Current Chef Solo configuration suggests single-node deployment - Ansible inventory will need to accommodate multi-node scenarios if scaling is required
- SSL certificates are self-signed for development - production deployment may require CA-signed certificates or Let's Encrypt automation
- Database passwords are acceptable for development but production deployment will require proper secret management
- UFW firewall rules are sufficient - enterprise environments may require more complex iptables or cloud security group configurations
- Vagrant development workflow will be maintained - Ansible provisioner configuration needed for Vagrantfile
- Git repository access for FastAPI tutorial assumes public repository - private repositories will require SSH key or token authentication
- System package availability assumes standard Ubuntu/CentOS repositories - custom package sources may require additional repository configuration
- Service management assumes systemd - older systems may require SysV init script alternatives