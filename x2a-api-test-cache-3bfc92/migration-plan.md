# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL certificate management, security hardening, and database configuration. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps not in cookbooks

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and nginx configuration templates
- **memcached (~> 6.0)**: Replace with community.general.memcached or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or geerlingguy.redis Ansible role
- **Chef Solo**: Replace with ansible-playbook execution model

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation needs migration to Ansible crypto modules or external certificate management
- **Hardcoded Credentials**: 
  - Redis password hardcoded in cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials hardcoded in fastapi-tutorial (`fastapi_password`)
  - Database connection strings in environment files
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban Configuration**: Jail configuration for nginx protection
- **Sysctl Security**: Kernel parameter tuning for security hardening

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook contains a Ruby block that manually edits Redis configuration files - this complex logic needs careful translation to Ansible
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple domains requires Ansible loops and certificate management
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment
- **Service Dependencies**: Ensuring proper startup order between PostgreSQL, Redis, and application services
- **Template Migration**: Converting ERB templates to Jinja2 format for nginx configuration

### Migration Order

1. **cache** (moderate complexity, foundational service)
2. **nginx-multisite** (high complexity due to SSL and security features, but independent)
3. **fastapi-tutorial** (moderate complexity, depends on database setup)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for the target environment (production may require Let's Encrypt or CA-signed certificates)
- The Redis configuration patching hack in the cache cookbook is still necessary in the target environment
- PostgreSQL will be installed locally rather than using an external database service
- The current hardcoded passwords are acceptable for the migration (should be moved to Ansible Vault in production)
- UFW firewall is the preferred firewall solution for the target environment
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- Systemd is available on the target systems for service management
- The current site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained