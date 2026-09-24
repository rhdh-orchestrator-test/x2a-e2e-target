# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration providing both memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning from GitHub, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations need careful migration to maintain access
- **Firewall Configuration**: UFW rules and fail2ban jail configurations require migration to ansible.posix.ufw and community.general.fail2ban modules
- **Credential Types per Module**:
  - nginx-multisite: SSL certificate paths, no embedded credentials
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), GitHub repository access (public)

### Technical Challenges

- **Complex Recipe Dependencies**: nginx-multisite cookbook has interdependent recipes (security → nginx → ssl → sites) that must maintain execution order in Ansible
- **Custom Resource Usage**: nginx-multisite uses a custom lineinfile resource that needs migration to ansible.builtin.lineinfile
- **Ruby Block Logic**: cache cookbook contains Ruby block for Redis configuration file manipulation that needs conversion to Ansible template or lineinfile operations
- **External Cookbook Dependencies**: Three external cookbooks (nginx, memcached, redisio) need replacement with equivalent Ansible modules or custom role development
- **File Template Migration**: Multiple ERB templates need conversion to Jinja2 format with proper variable substitution

### Migration Order

1. **cache** (low risk, standalone functionality, clear external dependencies)
2. **fastapi-tutorial** (moderate complexity, database integration, systemd service management)
3. **nginx-multisite** (high complexity, multiple interdependent recipes, security configurations, SSL management)

### Assumptions

- Target environments will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The GitHub repository for fastapi-tutorial remains publicly accessible
- UFW and fail2ban packages are available in target environment package repositories
- Systemd is the target service manager (no SysV init support required)
- The three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) will maintain the same DNS configuration
- Vagrant development environment workflow will be replaced with ansible-playbook execution or molecule testing