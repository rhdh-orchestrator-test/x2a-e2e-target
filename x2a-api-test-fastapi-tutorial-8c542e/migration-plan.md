# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail configuration - migrate using template module with fail2ban service management
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no stored credentials)

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules with proper regex patterns
- **Multi-site SSL Certificate Generation**: The nginx-multisite cookbook dynamically generates SSL certificates for each configured site - this pattern needs to be replicated using Ansible loops and the community.crypto collection
- **Chef Attribute Inheritance**: The solo.json overrides cookbook attributes for site configurations - this will need to be restructured using Ansible group_vars or host_vars
- **Service Dependency Management**: The FastAPI service depends on PostgreSQL being available - ensure proper task ordering and handlers in Ansible playbooks

### Migration Order

1. **cache** (low risk, standalone service)
   - Simple package installation and service configuration
   - Self-contained with minimal external dependencies
   - Good candidate for initial migration validation

2. **fastapi-tutorial** (moderate complexity)
   - Database setup and application deployment
   - Systemd service management
   - Environment configuration patterns

3. **nginx-multisite** (high complexity, security-critical)
   - Complex multi-site configuration
   - SSL certificate management
   - Security hardening and firewall rules
   - Should be migrated last due to security implications

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in Chef metadata
- Self-signed certificates are acceptable for the target environment (production environments may require CA-signed certificates)
- The current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault in production)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the 'main' branch will be stable
- The current site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the desired target state
- UFW firewall is the preferred firewall solution for the target environment
- The Redis configuration patching in the cache cookbook is still necessary and not resolved by newer Redis versions
- PostgreSQL will be installed locally rather than using an external database service
- The systemd service configuration for FastAPI is appropriate for the target environment
- The current Chef Solo execution model will be replaced by standard Ansible playbook execution
- No additional Chef cookbooks or dependencies exist beyond those specified in the Berksfile