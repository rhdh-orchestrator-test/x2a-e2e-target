# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
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

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed)

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules with proper regex patterns
- **Multi-site SSL Certificate Generation**: Dynamic SSL certificate creation for multiple domains requires loop-based certificate generation in Ansible with proper file permissions and ownership
- **Service Dependencies**: FastAPI application depends on PostgreSQL being ready - implement proper service ordering with Ansible handlers and wait_for conditions
- **Git Repository Management**: FastAPI cookbook clones and syncs git repositories - migrate to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificates being properly generated
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, systemd service management, and environment configuration

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or proper CA certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- The custom Redis configuration patching in the cache cookbook is still necessary and not resolved by newer Redis versions
- Systemd is available on target systems for service management (implied by FastAPI service configuration)
- The git repository for FastAPI tutorial (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- UFW firewall is the preferred firewall solution (rather than iptables or firewalld)
- The nginx sites configuration structure (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained in the Ansible version