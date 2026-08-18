# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (web server, application server, caching)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration (Memcached and Redis)
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef run list and node attributes configuration. Contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM for testing the Chef cookbooks.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata. The Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or use the `ansible.builtin.package` module to install Nginx and template configurations.
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or custom Ansible tasks.
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom Ansible tasks.

### Security Considerations

- **SSL Certificate Management**: 
  - The Chef cookbook generates self-signed certificates for development.
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto.x509_certificate` module.

- **Firewall Configuration**: 
  - UFW firewall is configured with specific rules.
  - Migration approach: Use Ansible's `community.general.ufw` module.

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured for intrusion prevention.
  - Migration approach: Use Ansible's `community.general.fail2ban` module or custom configuration templates.

- **SSH Hardening**: 
  - SSH configuration includes disabling root login and password authentication.
  - Migration approach: Use Ansible's `ansible.posix.sshd_config` module or the `ansible-hardening` role.

- **Vault/secrets management**:
  - Redis password is hardcoded in the Chef recipe (`redis_secure_password_123`).
  - PostgreSQL credentials are hardcoded in the FastAPI recipe.
  - Migration approach: Use Ansible Vault to encrypt sensitive values and use variables in templates.

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic generation of multiple virtual hosts with SSL.
  - Mitigation: Create Ansible templates that iterate through site configurations defined in variables.

- **SSL Certificate Generation**: 
  - Challenge: Replicating the self-signed certificate generation logic.
  - Mitigation: Use Ansible's `community.crypto` collection for certificate management.

- **PostgreSQL User and Database Creation**: 
  - Challenge: Ensuring idempotent database operations.
  - Mitigation: Use Ansible's `community.postgresql` collection for database management.

- **Service Dependencies**: 
  - Challenge: Maintaining proper service startup order and dependencies.
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper task ordering.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening (fail2ban, ufw)
   - Add virtual host configuration

2. **cache** (Priority 2)
   - Relatively simple configuration for Memcached and Redis
   - Ensure Redis password is stored securely in Ansible Vault

3. **fastapi-tutorial** (Priority 3)
   - More complex with database configuration and application deployment
   - Depends on proper database setup and configuration
   - Requires systemd service management

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora.
2. Self-signed certificates are acceptable for development, but production may require proper certificates.
3. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available.
4. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
5. The Vagrant development environment will be replaced with an equivalent Ansible-based setup.
6. The current Redis and Memcached configurations are sufficient for the application's needs.
7. The PostgreSQL database schema is managed by the FastAPI application's migrations, not by the infrastructure code.