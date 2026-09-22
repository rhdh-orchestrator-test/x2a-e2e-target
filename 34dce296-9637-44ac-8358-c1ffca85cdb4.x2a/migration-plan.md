# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file manipulation via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies from Chef Supermarket
- `solo.json`: Chef Solo run configuration with node attributes and run list - contains site-specific configuration overrides
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning for testing cookbook changes
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or custom Ansible tasks for memcached setup
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Multiple instances of embedded passwords requiring Ansible Vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: SSL certificate paths and private key locations need secure handling via Ansible Vault
- **SSH Security Configuration**: Root login disabling and password authentication controls require careful migration to maintain security posture
- **Firewall Rules**: UFW firewall configuration and fail2ban intrusion prevention need equivalent Ansible security modules

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby blocks for Redis configuration file manipulation that need conversion to Ansible lineinfile or template modules
- **Service Dependencies**: PostgreSQL service must be running before database user creation, requiring proper Ansible task ordering and handlers
- **Multi-site Configuration**: Dynamic site creation based on node attributes requires Ansible loops and variable templating
- **External Repository Dependencies**: Git repository cloning and Python virtual environment management need equivalent Ansible modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web infrastructure)
2. **cache** (high complexity due to Ruby blocks and dual service management)
3. **fastapi-tutorial** (moderate complexity, depends on database and application stack)

### Assumptions

- SSL certificates are manually managed and placed in standard system locations (/etc/ssl/certs, /etc/ssl/private)
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL service configuration uses default settings beyond user and database creation
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo execution model can be replaced with Ansible playbook execution without significant workflow changes
- Development and testing will continue to use Vagrant-based environments during migration
- The multi-site nginx configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) represents the production site structure