# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, including security hardening, SSL certificate management, and database configuration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, including custom Redis configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached integration, custom configuration patching via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv setup, PostgreSQL database/user creation, systemd service management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires Ansible Vault migration
- **Database credentials**: PostgreSQL user password "fastapi_password" in fastapi-tutorial cookbook needs vault protection
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH hardening**: Root login disable and password authentication disable require careful migration to maintain access
- **Firewall rules**: UFW configuration needs migration to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template requires migration to community.general.fail2ban module
- **Credential types identified**: Database passwords (2), Redis authentication (1), SSL certificates (3 sites)

### Technical Challenges
- **Ruby block workarounds**: The cache cookbook uses ruby_block to patch Redis configuration files - needs conversion to Ansible lineinfile or template modules
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready, requiring proper Ansible handler ordering
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple sites requires Ansible loops and conditional logic
- **Template variable mapping**: ERB templates need conversion to Jinja2 with variable name adjustments
- **Package manager differences**: Chef's package resource behavior may differ from Ansible's package module across distributions

### Migration Order
1. **cache** (low risk, foundational service) - Redis and Memcached are well-supported in Ansible
2. **fastapi-tutorial** (moderate complexity) - Straightforward application deployment with database setup
3. **nginx-multisite** (high complexity, security dependencies) - Complex SSL management and security hardening requires careful testing

### Assumptions
- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Current Redis configuration patches in ruby_block are still necessary and not resolved by newer Redis versions
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt or CA integration required)
- PostgreSQL will be installed locally rather than using external database services
- UFW firewall is the preferred firewall solution (not iptables or firewalld)
- SSH access will be maintained during security hardening migration
- Vagrant development environment will be replaced with Ansible-compatible local testing
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- Current attribute-based configuration in solo.json will translate to Ansible group_vars or host_vars structure