# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, templates, and variables. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom nginx configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef node attributes and run list configuration. Will be replaced by Ansible inventory variables and playbooks.
- `solo.rb`: Chef configuration file for Chef Solo. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in Vagrant. Will be replaced with Ansible provisioner in Vagrant.

### Target Details

Based on the source repository analysis:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile.
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration
- **PostgreSQL**: Currently installed directly in the fastapi-tutorial cookbook, will need direct installation or Ansible PostgreSQL role

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules to generate self-signed certificates or integrate with Let's Encrypt using the community.crypto collection
  - Current implementation generates self-signed certificates for each site

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to configure firewall rules
  - Current implementation enables UFW with specific rules for SSH, HTTP, and HTTPS

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to install and configure fail2ban with custom jail settings
  - Current implementation installs fail2ban with a custom jail.local template

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH settings
  - Current implementation disables root login and password authentication

- **Vault/secrets management**:
  - Redis password: Currently hardcoded in the cache cookbook as "redis_secure_password_123"
  - PostgreSQL credentials: Hardcoded in the fastapi-tutorial cookbook as username "fastapi" with password "fastapi_password"
  - Database connection string: Stored in plaintext in .env file
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically creates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible with_items/loop to iterate through site configurations defined in variables

- **Redis Configuration Patching**: 
  - Description: The current implementation uses a ruby_block to modify Redis configuration files after they're created
  - Mitigation strategy: Create a proper Redis configuration template in Ansible rather than modifying files after creation

- **Service Interdependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure services are configured in the correct order

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's openssl_* modules or consider integrating with Let's Encrypt for production environments

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database and user
   - Deploy application code from Git
   - Configure Python environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions.
2. Self-signed certificates are acceptable for development, but production may require proper certificates.
3. The security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current hardcoded credentials will be replaced with more secure solutions in the Ansible implementation.
6. The Vagrant development environment will be maintained for testing the Ansible playbooks.
7. The current directory structure in the target environment (/opt/fastapi-tutorial, /etc/ssl/certs, etc.) should be preserved.
8. The current service ports and configurations (Redis on 6379, FastAPI on 8000, etc.) should be maintained.