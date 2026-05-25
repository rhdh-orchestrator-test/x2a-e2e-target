# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No complex custom resources or libraries
- Standard infrastructure patterns are used
- Moderate number of templates and configurations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external) - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines the development VM configuration - can be adapted for Ansible testing
- `solo.json`: Contains Chef run list and node attributes - will be converted to Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration
- **Python 3 and pip**: Direct package installation via Ansible package module
- **PostgreSQL**: Replace with Ansible postgresql role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration approach: Use Ansible crypto modules for certificate generation or integrate with Let's Encrypt

- **Firewall Configuration**: 
  - UFW is configured in the Chef cookbook
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Configured in the Chef cookbook
  - Migration approach: Use Ansible to install and configure fail2ban

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible to configure SSH daemon

- **Vault/secrets management**:
  - Redis password is hardcoded in the Chef recipe
  - PostgreSQL password is hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates multiple virtual hosts based on node attributes
  - Mitigation: Use Ansible templates with loops to generate similar configuration

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Database User and Schema Creation**: 
  - Description: PostgreSQL user and database are created with direct commands
  - Mitigation: Use Ansible's postgresql_* modules for more idempotent database management

- **Service Configuration**: 
  - Description: Multiple services need to be configured and managed
  - Mitigation: Use Ansible's service module and handlers for service management

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear boundaries

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with Redis configuration

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Involves multiple components (database, application, service)

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for the migrated solution (or a clear path to proper certificates will be provided)
3. The same network topology and port configurations will be maintained
4. No changes to the application code or database schema are required
5. The Vagrant development environment should be preserved for testing
6. No specific CI/CD integration is required beyond what's currently implemented
7. The Redis password and PostgreSQL credentials will need to be securely stored in Ansible Vault
8. The FastAPI application will continue to be deployed from the same Git repository
9. The current security configurations (fail2ban, ufw, SSH hardening) should be maintained
10. No specific monitoring or logging solutions are required beyond what's currently implemented