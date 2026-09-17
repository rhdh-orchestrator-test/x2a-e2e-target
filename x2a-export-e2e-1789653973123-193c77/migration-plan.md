# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening, and firewall configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible integration)
- `vagrant-provision.sh`: Shell provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database credentials in environment files
- **SSL Certificate Management**: Self-signed certificate generation for development environments needs Ansible crypto modules
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban Integration**: Intrusion prevention system configuration with custom jail settings
- **Sysctl Security Tuning**: Kernel parameter hardening configurations

### Technical Challenges

- **Redis Configuration Patching**: Complex ruby block that modifies Redis config files post-installation requires custom Ansible lineinfile/replace tasks
- **Multi-Site SSL Management**: Dynamic SSL certificate generation per site needs loop-based Ansible tasks with proper certificate validation
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts, requiring proper Ansible handler ordering
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need careful Ansible file module configuration
- **Template Migration**: ERB templates need conversion to Jinja2 format with variable mapping

### Migration Order

1. **cache** (low risk, standalone service)
   - Simple package installation and service management
   - Redis configuration complexity is isolated
   - No dependencies on other cookbooks

2. **nginx-multisite** (moderate complexity, foundational)
   - Core web infrastructure needed by other services
   - Security configurations can be tested independently
   - SSL certificate generation is self-contained

3. **fastapi-tutorial** (high complexity, multiple dependencies)
   - Depends on PostgreSQL service availability
   - Complex Python environment management
   - Git repository integration and systemd service creation
   - Database initialization with credentials

### Assumptions

- Current Chef cookbooks are actively used in production environments
- SSL certificates are self-signed for development; production may use different certificate management
- PostgreSQL and Redis passwords are placeholders and will be replaced with proper secrets management
- UFW firewall rules are appropriate for target environments
- Python virtual environment approach is preferred over system-wide package installation
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Development environment (Vagrant) setup may need separate Ansible configuration
- Multi-platform support (Ubuntu/CentOS) requirement will be maintained in Ansible roles