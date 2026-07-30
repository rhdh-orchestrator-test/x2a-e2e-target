# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-service environment consisting of web servers (nginx), caching services (Redis and Memcached), and a FastAPI application with PostgreSQL database. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations
- SSL certificate management
- Database configuration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should:
  - Maintain the same certificate generation capability
  - Add support for Let's Encrypt integration
  - Ensure proper permissions on private keys

- **Firewall Configuration**: The current implementation uses UFW. Migration should:
  - Use ansible.posix.ufw module for Ubuntu targets
  - Use ansible.posix.firewalld module for Fedora/CentOS targets
  - Maintain the same rule set (SSH, HTTP, HTTPS)

- **SSH Hardening**: The current implementation disables root login and password authentication. Migration should:
  - Use ansible.posix.sshd_config module to apply the same settings
  - Ensure idempotent configuration

- **Fail2ban Integration**: The current implementation configures fail2ban for brute force protection. Migration should:
  - Install and configure fail2ban with the same jail settings
  - Ensure service is enabled and running

- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password"
  - Environment variables in .env file for FastAPI application

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates to generate site configurations. Migration should:
  - Create equivalent Jinja2 templates for Ansible
  - Ensure proper variable substitution
  - Maintain the same site structure and SSL configuration

- **Redis Configuration**: The current implementation includes a Ruby block to modify Redis configuration. Migration should:
  - Use Ansible's lineinfile or template module to achieve the same configuration
  - Ensure proper service restart handling

- **PostgreSQL User and Database Creation**: The current implementation uses shell commands. Migration should:
  - Use community.postgresql modules for more idempotent configuration
  - Maintain the same user permissions and database settings

- **Python Application Deployment**: The current implementation clones a Git repository and sets up a virtual environment. Migration should:
  - Use Ansible's git module for repository management
  - Create tasks for Python virtual environment setup
  - Ensure proper systemd service configuration

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it for access
   - Contains security configurations that should be applied first

2. **cache** (Priority 2)
   - Supporting services for the application
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment
   - Depends on PostgreSQL and potentially the cache services
   - Most complex with database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. The same network configuration (ports, IP addresses) will be maintained.
3. Self-signed certificates are acceptable for development/testing, but production deployment may require proper certificates.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current passwords and security settings are for development only and will be replaced with proper secrets management in production.
6. The Vagrant setup is primarily for development and testing, not for production deployment.
7. The migration will maintain the same service configuration but may improve security practices where appropriate.
8. The current Chef implementation does not use encrypted data bags or other advanced Chef features for secrets management.