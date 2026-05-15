# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom site templates

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

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `solo.json`: Contains the Chef run list and configuration data. Will be converted to Ansible group_vars or host_vars.
- `solo.rb`: Chef configuration file. Not needed in Ansible.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced by Ansible provisioner in Vagrantfile.

### Target Details

Based on the source repository analysis:

- **Operating System**: The configuration supports both Ubuntu (>=18.04) and CentOS (>=7.0) as indicated in cookbook metadata, but the Vagrantfile specifies Fedora 42 as the development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile.
- **Cloud Platform**: No specific cloud platform dependencies identified. The setup appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom implementation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or custom implementation
- **Python 3 and pip**: Use Ansible's package module for installation
- **PostgreSQL**: Use Ansible's `geerlingguy.postgresql` role or custom implementation

### Security Considerations

- **SSL Certificate Management**: 
  - The Chef cookbook generates self-signed certificates for development
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Current implementation uses execute resources to configure UFW
  - Migration approach: Use Ansible's `ufw` module for more declarative configuration

- **fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's `template` module for configuration files and `service` module for management

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or dedicated `ssh` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Custom Resource Migration**: 
  - The `lineinfile` custom resource in the nginx-multisite cookbook needs to be replaced with Ansible's native `lineinfile` module
  - Challenge: Ensuring identical behavior, especially with the backup functionality

- **Template Conversion**:
  - Chef ERB templates need to be converted to Jinja2 for Ansible
  - Challenge: Syntax differences and ensuring variable references are correctly translated

- **Idempotency Assurance**:
  - Some Chef recipes use `execute` resources with `not_if` guards
  - Challenge: Ensuring equivalent idempotency in Ansible tasks, possibly using `changed_when` and `failed_when` directives

- **Service Management**:
  - Chef uses the `service` resource with `supports` attribute for fine-grained control
  - Challenge: Mapping to Ansible's service module capabilities

### Migration Order

1. **nginx-multisite** (Priority 1):
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first
   - Moderate complexity with templates and custom resources

2. **cache** (Priority 2):
   - Depends on external cookbooks that need Galaxy role replacements
   - Contains sensitive data (Redis password) that needs secure handling
   - Lower complexity than the other modules

3. **fastapi-tutorial** (Priority 3):
   - Application deployment that depends on infrastructure being in place
   - Involves multiple components (Python, Git, PostgreSQL)
   - Higher complexity due to application deployment and database setup

### Assumptions

1. The target environment will continue to be Fedora-based as indicated in the Vagrantfile, though the cookbooks support Ubuntu and CentOS.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The hardcoded passwords in the recipes are for development only and will be replaced with Ansible Vault variables.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
6. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.
7. The PostgreSQL database configuration (user: fastapi, database: fastapi_db) will remain the same.
8. The Redis configuration (port 6379 with password authentication) will remain the same.