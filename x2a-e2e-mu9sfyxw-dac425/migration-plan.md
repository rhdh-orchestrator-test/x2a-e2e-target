# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL sites (test/ci/status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl kernel security parameters

**cache**:
- Description: Caching services configuration providing both Redis and Memcached with authentication and custom Redis configuration patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, Memcached service, Redis configuration file manipulation via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (likely for testing cookbook functionality)
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence for development)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management via ansible.builtin.systemd
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe code - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - implement proper certificate deployment with Ansible Vault for private keys
- **SSH Security Configuration**: SSH hardening (root login disabled, password auth disabled) implemented via sed commands - replace with ansible.posix.sshd_config module
- **Firewall Rules**: UFW firewall configuration via shell commands - migrate to community.general.ufw module
- **System Security**: Sysctl security parameters managed via template - use ansible.posix.sysctl module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that manipulates Redis configuration files with regex replacements - this custom logic needs to be replicated using Ansible's lineinfile or replace modules
- **Git Repository Management**: FastAPI cookbook clones from GitHub with sync action - implement using ansible.builtin.git module with proper change detection
- **Service Dependencies**: Complex service startup order (PostgreSQL before FastAPI, nginx after SSL setup) - use Ansible handlers and proper task ordering
- **Template Migration**: ERB templates (nginx.conf.erb, security.conf.erb, etc.) need conversion to Jinja2 format with equivalent variable substitution

### Migration Order

1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **fastapi-tutorial** (moderate complexity, database setup and application deployment)
3. **nginx-multisite** (high complexity, security configurations and multi-site SSL management with template dependencies)

### Assumptions

- SSL certificates are manually managed and placed in standard system paths (/etc/ssl/certs, /etc/ssl/private) - certificate provisioning process not defined in cookbooks
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable for production deployment
- PostgreSQL installation uses distribution packages rather than custom compilation or specific version requirements
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) resolve properly in the target environment's DNS configuration
- UFW firewall rules are appropriate for the target environment and don't conflict with existing network security policies
- The Redis configuration patching via ruby_block is necessary due to incompatibilities with the redisio cookbook version - this workaround logic needs investigation for root cause
- System-level security settings (sysctl parameters, SSH configuration) are compatible with organizational security policies and compliance requirements