# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file manipulation via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: Python FastAPI application deployment with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires assessment for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support required based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-role-nginx or community.general.nginx modules
- **memcached (~> 6.0)**: Replace with ansible-memcached role or package management tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis or geerlingguy.redis role
- **Chef Solo execution model**: Replace with ansible-playbook execution and inventory management

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths and configuration need secure handling in Ansible
- **SSH security configurations**: Root login disable and password authentication disable require careful migration to ensure access is maintained
- **Firewall rules**: UFW configuration needs translation to appropriate Ansible firewall modules
- **System security**: sysctl security parameters require validation during migration
- **Credential patterns per module**:
  - nginx-multisite: SSL certificate file references, no embedded secrets visible
  - cache: Redis password hardcoded in recipe
  - fastapi-tutorial: PostgreSQL password and database credentials hardcoded in recipe

### Technical Challenges

- **Ruby block configurations**: The cache cookbook uses Ruby blocks for Redis configuration file manipulation - requires translation to Ansible lineinfile or template modules
- **Multi-site SSL configuration**: Complex nginx virtual host setup with SSL requires careful template migration and certificate management
- **Service dependencies**: PostgreSQL must be running before FastAPI application setup - requires proper Ansible task ordering and handlers
- **Development environment**: Vagrant provisioning needs equivalent Ansible development setup
- **Cross-platform support**: Cookbooks support both Ubuntu and CentOS - Ansible playbooks must maintain this compatibility

### Migration Order

1. **cache** (low risk, foundational service) - Migrate caching services first as they have minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on cache services for optimal performance
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, should be migrated last due to service interdependencies

### Assumptions

- SSL certificates are managed externally or will be provided during Ansible deployment (certificate generation/management strategy not defined in current cookbooks)
- Database initialization and schema management for FastAPI application is handled by the application itself (not visible in Chef configuration)
- Network configuration and DNS resolution for *.cluster.local domains is managed outside of this configuration
- Development and production environments will use similar Ansible inventory structures
- Current Chef Solo execution model will be replaced with standard Ansible playbook execution against inventory
- External cookbook dependencies (nginx, memcached, redisio) have suitable Ansible Galaxy role equivalents available
- Security hardening requirements (fail2ban, UFW, SSH configuration) will maintain the same security posture in Ansible implementation
- Git repository access for FastAPI tutorial code will remain available and accessible from target systems
- Python package dependencies and virtual environment requirements will remain compatible with target systems