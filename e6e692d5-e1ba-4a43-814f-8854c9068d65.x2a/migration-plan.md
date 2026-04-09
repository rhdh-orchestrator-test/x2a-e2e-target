# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible Galaxy equivalents
- Security configurations need careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

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

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Defines the Chef policy with run list and cookbook dependencies
- `solo.json`: Configuration data for Chef solo, contains site configurations and security settings
- `solo.rb`: Chef solo configuration file defining cookbook paths and log settings
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

Based on the source repository analysis:

- **Operating System**: The cookbooks support both Ubuntu (>=18.04) and CentOS (>=7.0), with the Vagrant environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community role

### Security Considerations

- **Firewall (UFW)**: Migrate UFW rules to Ansible ufw module
- **Fail2ban**: Migrate fail2ban configuration to Ansible fail2ban role
- **SSH Hardening**: Migrate SSH security settings using Ansible's lineinfile or template modules
- **SSL Certificates**: Ensure secure generation and storage of SSL certificates
- **Redis Authentication**: Securely manage Redis password (currently hardcoded as 'redis_secure_password_123')
- **PostgreSQL Credentials**: Securely manage database credentials (currently hardcoded as 'fastapi_password')
- **Sysctl Security Settings**: Migrate kernel parameter hardening to Ansible sysctl module

### Technical Challenges

- **Multi-site Configuration**: Dynamically generating Nginx site configurations based on variables
- **SSL Certificate Management**: Generating and managing self-signed certificates for development
- **Service Dependencies**: Ensuring proper ordering of service deployments (PostgreSQL before FastAPI, etc.)
- **Configuration Templating**: Converting ERB templates to Jinja2 format for Ansible
- **Idempotency**: Ensuring all operations remain idempotent, especially database user/schema creation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement security hardening components
   - Implement SSL certificate management
   - Implement virtual host configuration

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL installation and configuration
   - Implement Python application deployment
   - Implement service management

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development environments
3. The same security hardening requirements will apply in the Ansible implementation
4. The FastAPI application source will remain available at the same Git repository
5. The current directory structure in the target environment (/opt/fastapi-tutorial, etc.) should be maintained
6. Redis and Memcached configurations don't require advanced clustering or replication
7. The current hardcoded credentials will be replaced with Ansible Vault or another secret management solution
8. The Nginx sites configuration will maintain the same domain structure (test.cluster.local, ci.cluster.local, status.cluster.local)