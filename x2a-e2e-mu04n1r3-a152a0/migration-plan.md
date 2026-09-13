# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, multiple virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local)

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom Redis configuration file manipulation, Memcached integration, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning (requires review for Ansible conversion)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **SSH Hardening**: Migration of SSH configuration changes (PermitRootLogin no, PasswordAuthentication no) to ansible.posix.sshd_config module
- **Firewall Management**: UFW commands need conversion to community.general.ufw module with proper rule definitions
- **SSL Certificate Management**: Self-signed certificate generation requires community.crypto.openssl_privatekey and community.crypto.x509_certificate modules
- **Fail2ban Configuration**: Template-based jail.local configuration needs conversion to community.general.ini_file or template module
- **Sysctl Security**: System kernel parameter tuning via ansible.posix.sysctl module
- **Vault/secrets management**: 
  - **cache module**: Hardcoded Redis password ('redis_secure_password_123') in recipe - requires Ansible Vault encryption
  - **fastapi-tutorial module**: PostgreSQL password ('fastapi_password') and database credentials in plain text - requires Ansible Vault
  - **nginx-multisite module**: SSL certificate generation with hardcoded subject information - consider parameterization
  - Total credential instances: 3 hardcoded passwords requiring vault migration

### Technical Challenges

- **Complex Recipe Dependencies**: nginx-multisite cookbook uses include_recipe pattern with 4 sub-recipes requiring careful role/task organization in Ansible
- **Ruby Block Logic**: cache cookbook contains Ruby block for Redis configuration file manipulation - needs conversion to ansible.builtin.replace or ansible.builtin.lineinfile tasks
- **Dynamic Site Generation**: nginx-multisite dynamically creates virtual hosts from node attributes - requires Ansible loops and template generation
- **Service Interdependencies**: FastAPI application depends on PostgreSQL service startup - requires proper task ordering and handlers in Ansible
- **File Resource Management**: Multiple cookbook_file and template resources need conversion to ansible.builtin.copy and ansible.builtin.template modules

### Migration Order

1. **cache** (low risk, standalone service, clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies, systemd service)
3. **nginx-multisite** (high complexity, security configurations, multi-service dependencies)

### Assumptions

- Chef Solo execution model can be replaced with Ansible playbook execution against target hosts
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with Ansible modules or custom tasks
- Self-signed SSL certificates are acceptable for the target environment (production may require CA-signed certificates)
- PostgreSQL installation and configuration from fastapi-tutorial cookbook assumes local database deployment
- UFW firewall rules and fail2ban configurations are appropriate for the target security requirements
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during and after migration
- Target systems have systemd for service management (inferred from systemd service file creation)
- Ruby block configuration manipulation in cache cookbook can be replaced with Ansible file manipulation modules without functional loss