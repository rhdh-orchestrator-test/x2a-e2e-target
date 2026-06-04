# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible equivalents
- Security configurations need careful migration
- Secrets management needs to be implemented in Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `Vagrantfile`: Defines the development VM using Fedora 42. Will need to be updated to use Ansible provisioner instead of Chef.
- `solo.json`: Chef node attributes and run list. Will be converted to Ansible group_vars or host_vars.
- `solo.rb`: Chef configuration file. No direct Ansible equivalent needed.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Will be replaced by Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or create a custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or create a custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or integrate with Let's Encrypt using ansible-role-certbot

- **Firewall Configuration (UFW)**:
  - Current implementation configures UFW with specific rules
  - Migration approach: Use Ansible's ufw module to configure the same rules

- **Fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's template module to create fail2ban configuration files

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH settings

- **Sysctl Security Settings**:
  - Current implementation applies security-related sysctl settings
  - Migration approach: Use Ansible's sysctl module to apply the same settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Move all credentials to Ansible Vault and reference them in playbooks

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates for Nginx site configurations and use with_items to iterate through site definitions

- **Redis Configuration Hack**:
  - Challenge: The Chef recipe includes a hack to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible that doesn't require post-processing

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and the 'notify' mechanism to ensure proper sequencing

- **SSL Certificate Generation**:
  - Challenge: Replicating the self-signed certificate generation logic
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with proper permissions

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Implement multi-site configuration

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL database setup
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (vs. integrating with Let's Encrypt or other CA).
3. The same security hardening measures are required in the Ansible implementation.
4. The FastAPI application repository will remain available at the specified URL.
5. The Redis configuration hack is necessary due to compatibility issues that may need to be addressed in the Ansible version.
6. The current Chef implementation does not use encrypted data bags or other secret management, so all secrets are in plaintext.
7. The Vagrant development environment should be preserved with equivalent functionality.
8. No CI/CD pipeline integration is required as part of the migration.