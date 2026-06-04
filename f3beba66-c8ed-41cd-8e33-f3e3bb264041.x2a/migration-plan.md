# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, attributes, and custom resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The Chef cookbooks are well-structured and follow standard patterns
- No complex custom resources or libraries
- Clear separation of concerns between cookbooks
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Defines the Chef run list and node attributes
  - Migration consideration: Convert to Ansible group_vars or host_vars
  
- `solo.rb`: Chef Solo configuration
  - Migration consideration: Replace with ansible.cfg
  
- `Vagrantfile`: Defines the development VM configuration
  - Migration consideration: Update to use Ansible provisioner instead of Chef
  
- `vagrant-provision.sh`: Shell script to install Chef and run cookbooks
  - Migration consideration: Replace with Ansible provisioning commands

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile)
  - Also supports Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx_* modules or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role

### Security Considerations

- **SSL Certificate Management**:
  - Migration approach: Use Ansible's openssl_* modules to generate self-signed certificates
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's community.general.ufw module

- **Fail2ban Configuration**:
  - Migration approach: Create Ansible tasks to install and configure fail2ban

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile module to modify sshd_config

- **Vault/secrets management**:
  - Redis password in cache cookbook: Store in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Store in Ansible Vault
  - Count: 2 credentials detected (Redis auth password, PostgreSQL user password)

### Technical Challenges

- **Custom Resource Migration**:
  - Challenge: The nginx-multisite cookbook includes a custom `lineinfile` resource
  - Mitigation: Replace with Ansible's built-in lineinfile module

- **Template Conversion**:
  - Challenge: Converting ERB templates to Jinja2 format
  - Mitigation: Carefully map ERB syntax to Jinja2, especially for conditional statements

- **Service Management**:
  - Challenge: Ensuring proper service dependencies and startup order
  - Mitigation: Use Ansible's meta dependencies between roles and handlers for service notifications

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it
   - Contains security configurations that should be applied first

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity
   - Required by the application

3. **fastapi-tutorial** (Priority 3)
   - Application deployment
   - Depends on PostgreSQL
   - Most complex with multiple components (Python, Git, PostgreSQL, systemd)

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed SSL certificates are acceptable (production environments may require proper certificates)
3. The same directory structure for web content will be maintained
4. The FastAPI application repository will remain available at the specified URL
5. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. Redis and Memcached configurations don't require advanced tuning beyond what's in the current cookbooks
7. The PostgreSQL database schema is managed by the FastAPI application, not by the infrastructure code
8. The current Vagrant development workflow should be preserved but with Ansible instead of Chef