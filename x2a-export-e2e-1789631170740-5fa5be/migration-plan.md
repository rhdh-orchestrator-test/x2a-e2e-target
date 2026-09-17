# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl kernel parameter tuning

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication and custom Redis configuration patches
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, including virtual environment setup and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (not examined but likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Shell script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be generic Linux deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **Chef Supermarket dependencies**: All external cookbooks need equivalent Ansible Galaxy roles or custom implementation

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes need secure deployment mechanism
- **SSH security hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW configuration with specific port allowances (22, 80, 443) requires ansible.posix.ufw module
- **Fail2ban configuration**: Intrusion prevention settings in ERB templates need conversion to Jinja2
- **Sysctl security parameters**: Kernel security tuning requires ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses Ruby blocks to manually edit Redis config files - this complex file manipulation needs conversion to Ansible lineinfile or template modules
- **Multi-site nginx configuration**: Template-driven virtual host generation with SSL requires careful Jinja2 template conversion and loop handling
- **PostgreSQL database initialization**: Database and user creation commands need conversion to community.postgresql.* modules with proper idempotency
- **Systemd service management**: Custom service file creation and daemon-reload handling requires ansible.builtin.systemd module
- **Git repository management**: FastAPI application deployment via git clone needs ansible.builtin.git module with proper update handling

### Migration Order

1. **cache** (low risk, foundational service) - Start with caching services as they have fewer dependencies and simpler configuration
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but straightforward service management
3. **nginx-multisite** (high complexity, security dependencies) - Complex multi-site configuration with security hardening that depends on other services being available

### Assumptions

- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private - certificate provisioning process not defined in cookbooks
- The FastAPI tutorial repository at https://github.com/dibanez/fastapi_tutorial.git remains accessible and stable
- PostgreSQL installation uses distribution packages rather than custom compilation
- UFW firewall is the preferred firewall solution (no iptables rules defined)
- The target environment has internet access for package installation and git repository cloning
- Systemd is the service manager on target systems (no SysV init support)
- The "cluster.local" domain names (test.cluster.local, ci.cluster.local, status.cluster.local) are resolvable in the target environment
- Redis configuration patching is still necessary in the target environment (the Ruby block hack suggests compatibility issues with the redisio cookbook)
- Development workflow uses Vagrant but production deployment method is not specified
- No backup or disaster recovery procedures are defined for the PostgreSQL database or Redis data