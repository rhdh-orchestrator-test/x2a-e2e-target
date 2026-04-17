# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles, addressing security configurations, and maintaining the multi-environment deployment capabilities.

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
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

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

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio) - will be replaced with Ansible Galaxy requirements.yml
- `Policyfile.rb`: Defines the run list and cookbook dependencies - will be replaced with Ansible playbooks
- `solo.json`: Contains node attributes and run list - will be converted to Ansible inventory variables
- `solo.rb`: Chef Solo configuration - will be replaced with ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom implementation
- **ssl_certificate (~> 2.1)**: Replace with Ansible modules for SSL certificate management (openssl_*, community.crypto.*)
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom implementation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom implementation

### Security Considerations

- **fail2ban configuration**: Migrate fail2ban configuration to Ansible using the appropriate modules
  - Migration approach: Use Ansible template module to create fail2ban configuration files
  
- **ufw firewall rules**: Convert ufw commands to Ansible ufw module calls
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **SSH hardening**: Migrate SSH security configurations
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH daemon

- **SSL certificate management**: Convert self-signed certificate generation
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL password in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Recommendation: Move these to Ansible Vault

### Technical Challenges

- **Multi-site Nginx configuration**: The dynamic generation of Nginx site configurations based on node attributes needs careful migration
  - Mitigation: Use Ansible's template module with proper looping over host variables

- **Self-signed SSL certificates**: The current implementation generates self-signed certificates for each site
  - Mitigation: Use Ansible's openssl_certificate module with proper conditionals

- **PostgreSQL user and database creation**: The current implementation uses shell commands
  - Mitigation: Replace with Ansible's postgresql_* modules for better idempotence

- **Redis configuration hacks**: The current implementation includes a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. The same network configuration will be maintained (private network with IP 192.168.121.10)
3. Self-signed certificates are acceptable for development/testing purposes
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. The Redis and Memcached configurations do not require advanced tuning beyond what's currently implemented
7. The PostgreSQL database will continue to be hosted on the same server as the application
8. The current directory structure (/opt/fastapi-tutorial, /var/www/sites) will be maintained
9. The systemd service configuration for the FastAPI application will remain similar
10. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved