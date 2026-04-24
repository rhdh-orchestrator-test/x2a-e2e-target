# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are explicitly defined in Berksfile
- Security configurations are present and need careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4). These will need to be replaced with Ansible Galaxy roles or custom roles.
- `solo.json`: Defines the run list and configuration parameters for Chef Solo. Will be replaced by Ansible inventory and group/host variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced with Ansible provisioning.

### Target Details

- **Operating System**: The repository targets both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in the cookbook metadata files. However, the Vagrantfile uses Fedora 42 as the development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile.
- **Cloud Platform**: No specific cloud platform configurations were found. The setup appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy `geerlingguy.nginx` role or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy `geerlingguy.redis` or `DavidWittman.redis` role
- **PostgreSQL**: Use Ansible Galaxy `geerlingguy.postgresql` role for database setup

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or integrate with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration (UFW)**:
  - Current implementation uses UFW with explicit allow rules for SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `ufw` module or `geerlingguy.firewall` role

- **Fail2ban Integration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to configure fail2ban or use a dedicated Galaxy role

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or `dev-sec.ssh-hardening` Galaxy role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault to encrypt sensitive data and use variables for credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates for Nginx site configurations and use with_items to iterate through site definitions

- **SSL Certificate Generation**:
  - Challenge: Ensuring secure certificate generation and management
  - Mitigation: Use Ansible's `openssl_*` modules with proper error handling and idempotence checks

- **Database Initialization**:
  - Challenge: Ensuring idempotent database and user creation
  - Mitigation: Use Ansible's PostgreSQL modules with proper conditionals

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and proper task ordering with dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Moderate complexity with security configurations
   - Start with basic Nginx installation, then add virtual hosts and SSL

2. **cache** (Priority 2)
   - Independent service with external dependencies
   - Relatively simple configuration
   - Focus on securing Redis with proper password management

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Higher complexity with database setup and application deployment
   - Ensure proper secrets management for database credentials

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates.
3. The current security configurations are appropriate and should be maintained in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Redis password and PostgreSQL credentials will be managed more securely in the Ansible implementation.
6. The Vagrant development environment will be maintained for testing the Ansible playbooks.
7. No specific monitoring or logging solutions are required beyond the basic Nginx logging.
8. The current setup does not include load balancing or high availability configurations.