# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with node attributes and run list - contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.lineinfile for configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSH security configurations**: Root login disable and password authentication disable require careful migration to ensure access is maintained
- **SSL certificate management**: Certificate paths are configured but actual certificate deployment method needs clarification
- **Firewall rules**: UFW configuration includes SSH, HTTP, and HTTPS rules that must be preserved during migration
- **Fail2ban configuration**: Intrusion prevention settings need template migration from ERB to Jinja2

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a ruby_block hack for Redis configuration that needs to be replaced with proper Ansible configuration management
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible handler and dependency management
- **Git repository management**: FastAPI tutorial cloning and updates need to be handled with ansible.builtin.git module
- **Virtual environment management**: Python venv creation and pip installations require careful ordering and idempotency checks
- **Template migration**: ERB templates (nginx.conf.erb, security.conf.erb, etc.) need conversion to Jinja2 format

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web infrastructure)
2. **cache** (low complexity, independent caching services)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- SSL certificates are managed externally and only paths need to be configured (actual certificate deployment method not visible in current cookbooks)
- The ruby_block hack in Redis configuration indicates potential upstream cookbook limitations that may not exist in Ansible Redis modules
- Development environment uses Vagrant but production deployment method is not specified
- Database credentials are acceptable to be stored in Ansible Vault rather than external secret management system
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo execution model can be replaced with Ansible playbook execution without significant workflow changes
- Multi-platform support (Ubuntu/CentOS) requirement will be maintained in Ansible implementation