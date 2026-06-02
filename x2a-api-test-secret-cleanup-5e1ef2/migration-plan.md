# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- The repository has a moderate number of cookbooks with clear responsibilities
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful handling
- Secrets management needs to be implemented using Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development in Vagrant.
- **Virtual Machine Technology**: Vagrant with libvirt provider for development environment.
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible Galaxy `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy `geerlingguy.redis` role or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or `community.crypto.x509_certificate`

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `community.general.ufw` module

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible Galaxy `geerlingguy.security` role or create a custom role using `template` module

- **SSH Hardening**:
  - Migration approach: Use Ansible Galaxy `dev-sec.ssh-hardening` role or create custom tasks

- **Vault/secrets management**:
  - Redis password in cache cookbook: Store in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Store in Ansible Vault
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple Nginx sites
  - Mitigation: Create Ansible templates with similar structure and use Ansible variables for site configuration

- **Redis Configuration Workaround**:
  - Description: The Chef cookbook includes a hack to fix Redis configuration
  - Mitigation: Use Ansible templates with proper configuration or find a more maintained Redis role

- **Service Orchestration**:
  - Description: Ensuring proper service restart ordering (e.g., PostgreSQL before FastAPI application)
  - Mitigation: Use Ansible handlers and the `notify` mechanism with proper dependencies between tasks

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's crypto modules or consider integrating with Let's Encrypt for production environments

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement security hardening
   - Configure SSL certificate generation
   - Set up virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions.
2. Self-signed certificates are acceptable for the migrated solution, or a strategy for proper certificate management will be provided.
3. The Vagrant development environment will be replaced with an equivalent Ansible-based local development solution.
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate and should be maintained in the Ansible implementation.
5. Redis and PostgreSQL passwords in the current implementation are examples and will be replaced with proper secret management in Ansible.
6. The FastAPI application repository URL and structure will remain the same.
7. The current directory structure for web content and application code will be maintained.