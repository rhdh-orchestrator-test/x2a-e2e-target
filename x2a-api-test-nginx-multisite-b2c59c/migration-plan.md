# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site virtual host configuration, SSL certificate generation, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template, and ansible.builtin.service modules for Redis configuration and management

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using ansible.builtin.openssl_* modules or community.crypto collection
- **SSH Hardening**: Root login disabled and password authentication disabled via direct file modification - use ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via shell commands - use community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - use ansible.builtin.template with Jinja2 templates
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually patches Redis configuration files by removing specific lines - this will need to be replaced with proper Ansible template management or lineinfile modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites requires loop-based certificate creation in Ansible
- **Service Dependencies**: PostgreSQL must be running before database user creation, and systemd daemon-reload is required before service management
- **File Permissions**: SSL private keys require specific ownership (root:ssl-cert) and permissions (640) that must be preserved

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal dependencies and clear service boundaries
2. **nginx-multisite** (moderate complexity) - Migrate web server configuration including security hardening, as it provides the foundation for application access
3. **fastapi-tutorial** (high complexity, application dependencies) - Migrate application deployment last as it depends on database setup and has the most complex service management requirements

### Assumptions

- The target environment will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production deployments may require proper CA-signed certificates)
- The Redis configuration patching in the cache cookbook addresses specific version compatibility issues that may not be present in newer Redis versions
- PostgreSQL service is managed by the system package manager and not containerized
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- UFW firewall is the preferred firewall solution (rather than iptables or firewalld)
- The three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete site configuration requirements
- Static HTML files for each site are sufficient (no dynamic content generation required)
- Systemd is the service manager on the target systems
- The ssl-cert group exists or can be created on target systems for SSL key management