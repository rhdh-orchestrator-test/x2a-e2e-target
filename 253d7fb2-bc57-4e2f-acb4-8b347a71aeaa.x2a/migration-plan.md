# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with external dependencies, SSL certificate management, and comprehensive security hardening. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached setup, including custom Redis configuration fixes and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (redis_secure_password_123), Memcached integration, custom Redis config file manipulation, log directory creation

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban integration, UFW firewall configuration, security headers, HSTS, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Dependency management for external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Node configuration with site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration for local cookbook execution
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - implement with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - implement with ansible.posix.sshd_config
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Jail configuration for nginx protection - use community.general.fail2ban
- **Security headers**: Comprehensive HTTP security headers in nginx configuration
- **Credential types per module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed for development)

### Technical Challenges

- **Redis configuration manipulation**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules
- **Multi-site SSL management**: Dynamic SSL certificate generation and nginx site configuration for multiple domains requires careful template management and certificate lifecycle handling
- **Service dependencies**: FastAPI service depends on PostgreSQL being ready, requiring proper task ordering and service state verification
- **Template complexity**: The nginx site configuration template includes conditional SSL logic that needs to be preserved in Jinja2 templates

### Migration Order

1. **cache** (low risk, high value): Straightforward service installation with well-defined external dependencies
2. **nginx-multisite** (moderate complexity): Core infrastructure component with security configurations but manageable template migration
3. **fastapi-tutorial** (high complexity, dependencies): Application deployment with database setup, requires cache and nginx to be functional for full stack operation

### Assumptions

- The current Redis password and PostgreSQL credentials are development/testing values that will be replaced with Vault-managed secrets in production
- Self-signed certificates are acceptable for development environments, but production will require integration with proper CA or Let's Encrypt
- The UFW firewall rules are sufficient for the target environment security requirements
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the main branch is stable
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) represent the actual target hostnames for the production environment
- The Ruby block manipulation of Redis configuration files indicates specific Redis version compatibility issues that may need investigation in the target Ansible environment
- The systemd service configuration for FastAPI assumes a systemd-based target system (Ubuntu 18.04+/CentOS 7+)