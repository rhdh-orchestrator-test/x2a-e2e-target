# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificate generation, HTTP to HTTPS redirects, security headers, fail2ban integration, UFW firewall rules, SSH configuration hardening

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication, custom logging, and configuration file manipulation
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file post-processing via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site definitions, SSL settings, and security parameters
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Vagrant provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic infrastructure

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and configuration templates
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **External cookbook dependencies**: All external Chef Supermarket cookbooks need replacement with equivalent Ansible modules or custom playbook tasks

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe code and need migration to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation logic needs conversion to ansible.builtin.openssl_* modules
- **SSH configuration**: SSH hardening (root login disable, password auth disable) requires careful migration to maintain security posture
- **Firewall rules**: UFW firewall configuration needs migration to community.general.ufw module
- **System security**: Sysctl security parameters and fail2ban configuration require template migration
- **File permissions**: SSL certificate file permissions (ssl-cert group) and service user configurations need preservation

### Technical Challenges

- **Ruby block logic**: The cache cookbook contains Ruby code blocks for Redis configuration file manipulation that need conversion to Ansible file manipulation modules or custom filters
- **Complex template logic**: ERB templates with conditional SSL configuration require conversion to Jinja2 templates with equivalent logic
- **Service dependencies**: PostgreSQL service must be running before database user creation, requiring proper Ansible task ordering and handlers
- **Multi-site configuration**: Dynamic site generation from node attributes needs conversion to Ansible loops and variable structures
- **External repository cloning**: Git repository management needs migration to ansible.builtin.git module with proper authentication handling

### Migration Order

1. **cache** (low risk, foundational service) - Migrate caching services first as they have fewer dependencies and provide foundation for other services
2. **fastapi-tutorial** (moderate complexity) - Migrate application deployment after caching infrastructure is established
3. **nginx-multisite** (high complexity, security-critical) - Migrate web server configuration last due to SSL, security, and multi-site complexity

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+) as defined in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production environments may require CA-signed certificates)
- The current Redis and PostgreSQL password management approach is acceptable (hardcoded passwords will be migrated to Ansible Vault)
- The multi-site configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved in the Ansible implementation
- Systemd is available on target systems for service management (implied by the FastAPI systemd service configuration)
- The current security hardening approach (fail2ban, UFW, SSH configuration) meets target environment requirements
- Git repository access for the FastAPI tutorial repository will remain available and accessible from target systems
- The Ruby block configuration manipulation in the cache cookbook represents necessary configuration changes that cannot be achieved through standard Redis configuration parameters