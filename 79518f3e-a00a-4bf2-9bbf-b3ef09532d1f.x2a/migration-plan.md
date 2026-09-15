# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate management, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified (local development environment focus)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package for Redis installation and configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled and password authentication disabled via direct file modification - use ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via shell commands - replace with community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate templates to Jinja2 format
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no stored credentials but certificate management

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook uses a Ruby block to manually edit Redis configuration files post-installation - this will need to be replaced with proper Ansible template management or lineinfile modules
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple sites requires careful loop handling in Ansible with proper certificate validation
- **Service Dependencies**: PostgreSQL must be running before database creation, and nginx must reload after configuration changes - ensure proper task ordering and handlers
- **Template Migration**: ERB templates need conversion to Jinja2 format, particularly the nginx.conf.erb and security configuration templates
- **Package Management**: Cross-platform support (Ubuntu/CentOS) requires conditional package installation logic

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Core web server infrastructure with security hardening
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- The current Chef Solo setup suggests a single-node deployment model - Ansible inventory will need to be designed for the target deployment architecture
- SSL certificates are currently self-signed for development - production deployment may require integration with Let's Encrypt or corporate CA
- Database credentials and Redis passwords will need to be externalized to Ansible Vault before production use
- The Vagrant development environment suggests local testing capability should be maintained in the Ansible version
- UFW firewall rules assume a standard web server deployment - additional ports may be needed for monitoring or other services
- The multi-platform support (Ubuntu/CentOS) indicates the need for OS-specific variable files and conditional task execution
- Git repository access for the FastAPI tutorial assumes public repository access - private repositories will require SSH key or token management
- System service management assumes systemd - older systems may require different service management approaches