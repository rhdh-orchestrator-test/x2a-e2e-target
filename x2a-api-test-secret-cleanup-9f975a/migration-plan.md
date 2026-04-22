# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total**: 7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and must be carefully migrated
- Database and application configurations contain credentials that will need secure handling

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall), custom Nginx configurations

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
  - Migration considerations: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Chef node configuration with run list and attributes
  - Migration considerations: Convert to Ansible group_vars or host_vars
  
- `solo.rb`: Chef configuration file
  - Migration considerations: Replace with ansible.cfg
  
- `Vagrantfile`: Defines development VM for testing
  - Migration considerations: Update to use Ansible provisioner instead of Chef
  
- `vagrant-provision.sh`: Shell script to install Chef and run cookbooks
  - Migration considerations: Replace with Ansible provisioning commands

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Current approach configures UFW with specific rules
  - Migration approach: Use Ansible's ufw module

- **Fail2ban Configuration**:
  - Current approach installs and configures fail2ban
  - Migration approach: Use Ansible's template module with fail2ban configuration templates

- **SSH Hardening**:
  - Current approach modifies sshd_config to disable root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or community.general.ssh_config module

- **Vault/secrets management**:
  - Credentials detected:
    - Redis password in cache/recipes/default.rb
    - PostgreSQL user/password in fastapi-tutorial/recipes/default.rb
    - Database connection string in .env file
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Preserving the dynamic generation of site configurations
  - Mitigation: Use Ansible's with_items/loop constructs with templates

- **SSL Certificate Generation**:
  - Challenge: Replicating the conditional SSL certificate generation logic
  - Mitigation: Use Ansible's community.crypto.x509_certificate module with proper check_mode support

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible's handlers and meta dependencies between roles

- **Custom Configuration Files**:
  - Challenge: Preserving the custom configuration templates and their variables
  - Mitigation: Convert ERB templates to Jinja2 format, maintaining variable structure

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, standalone service)
   - Create Memcached role
   - Create Redis role with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create PostgreSQL role
   - Create Python application deployment role
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (or compatible RPM-based distributions)
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The same security hardening requirements will apply in the Ansible version
4. The FastAPI application repository will remain available at the specified URL
5. The directory structure for web content and application files will remain the same
6. No additional monitoring or logging solutions are required beyond what's in the current Chef implementation
7. The Redis and Memcached configurations don't require clustering or advanced features
8. The PostgreSQL database doesn't require replication or backup configuration
9. The current Vagrant-based development workflow should be preserved