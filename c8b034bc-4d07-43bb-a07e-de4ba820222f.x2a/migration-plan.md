# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Moderate number of templates and configurations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio) - will be replaced by Ansible Galaxy requirements
- `Policyfile.rb`: Defines the run list and cookbook dependencies - will be replaced by Ansible playbook structure
- `solo.json`: Contains node attributes and configuration data - will be migrated to Ansible variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Shell script for provisioning - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant for testing
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible's openssl modules for certificate generation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW - migrate to Ansible's ufw module
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **SSL Certificate Management**: Ensure proper handling of SSL certificates and private keys
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - SSL certificate private keys stored in /etc/ssl/private
  - Total credentials detected: 2 hardcoded passwords, plus SSL certificate keys

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of site configurations is properly implemented in Ansible
- **SSL Certificate Generation**: Implement self-signed certificate generation for development environments
- **Service Dependencies**: Maintain proper ordering of service installations and configurations
- **Idempotency**: Ensure all operations are idempotent, particularly database user creation and Git repository cloning

### Migration Order

1. **nginx-multisite** (Priority 1): Foundation for web services, relatively self-contained
2. **cache** (Priority 2): Dependent services that other applications may need
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on PostgreSQL

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. The Vagrant development environment will be maintained for testing
3. Self-signed SSL certificates are acceptable for development (production would likely use different certificate sources)
4. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution
5. The FastAPI application source will continue to be available at the specified Git repository
6. Redis and Memcached configurations don't require advanced clustering or high availability features
7. The current hardcoded credentials will be replaced with Ansible Vault or another secure credential management solution
8. The current directory structure in the target system (/opt/fastapi-tutorial, /etc/ssl/, etc.) should be maintained