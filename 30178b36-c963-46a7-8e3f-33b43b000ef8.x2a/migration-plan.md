# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- The repository has well-structured Chef cookbooks with clear separation of concerns
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom Nginx configurations

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached configuration, Redis with password authentication, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
- `solo.json`: Chef configuration data and run list
  - Migration consideration: Convert to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file
  - Migration consideration: Replace with ansible.cfg
- `Vagrantfile`: Defines the development VM configuration
  - Migration consideration: Update to use Ansible provisioner instead of Chef
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
  - Migration consideration: Replace with Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>=18.04) and CentOS (>=7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or dedicated Ansible Galaxy role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis Galaxy role (e.g., geerlingguy.redis)
- **Python/FastAPI dependencies**: Use Ansible's `pip` module for Python package management

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integrating with Let's Encrypt via Ansible community modules

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible templates to configure fail2ban similar to current Chef templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or dedicated ssh hardening role

- **Vault/secrets management**:
  - Credentials detected:
    - Redis password in cache/recipes/default.rb: "redis_secure_password_123"
    - PostgreSQL user/password in fastapi-tutorial/recipes/default.rb: "fastapi"/"fastapi_password"
    - Database connection string in .env file
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible templates with loops over site definitions in variables

- **SSL Certificate Management**: 
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file and openssl modules with appropriate permissions

- **Service Orchestration**: 
  - Challenge: Maintaining proper service restart triggers when configurations change
  - Mitigation: Use Ansible handlers to restart services only when needed

- **Database Initialization**: 
  - Challenge: Idempotent database and user creation
  - Mitigation: Use Ansible's PostgreSQL modules with appropriate when conditions

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Create base Nginx role with security hardening
   - Implement virtual host configuration templates

2. **cache** (Priority 2)
   - Implement Memcached and Redis roles
   - Configure authentication and security settings

3. **fastapi-tutorial** (Priority 3)
   - Implement Python application deployment
   - Configure PostgreSQL database
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations meet performance requirements
6. The Vagrant development environment should be preserved with similar networking configuration
7. No custom Nginx modules or complex configurations beyond what's visible in the templates
8. No external service dependencies beyond what's explicitly configured in the cookbooks