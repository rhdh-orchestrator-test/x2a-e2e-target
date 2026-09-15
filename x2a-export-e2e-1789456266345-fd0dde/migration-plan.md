# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file post-processing, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git-based application deployment, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Vagrant provisioning script for Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined but certificate provisioning not automated - implement proper certificate management with ansible.builtin.copy or community.crypto modules
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations in Ansible
- **Firewall rules**: UFW firewall with specific port allowances (SSH, HTTP, HTTPS) - migrate to community.general.ufw module
- **Fail2ban configuration**: Intrusion prevention system - migrate to ansible.builtin.template with fail2ban configuration
- **System security tuning**: sysctl security parameters - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Complex Redis configuration post-processing**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need custom Ansible logic using ansible.builtin.lineinfile with regex patterns
- **Multi-site nginx configuration**: Dynamic site generation based on node attributes requires Ansible template loops and proper variable structure
- **Database initialization**: PostgreSQL user and database creation with proper privilege management needs careful translation to community.postgresql modules
- **Service dependencies**: Proper ordering of PostgreSQL → FastAPI service startup requires Ansible handlers and dependency management
- **Git-based deployment**: Application code deployment from Git repository needs ansible.builtin.git module with proper change detection

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational infrastructure)
2. **cache** (low-moderate complexity, independent services)
3. **fastapi-tutorial** (highest complexity, depends on database and potentially cache services)

### Assumptions

- SSL certificates are manually managed and placed in standard system locations (/etc/ssl/certs, /etc/ssl/private) - certificate provisioning automation is not included in current Chef implementation
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable for deployment
- PostgreSQL installation uses distribution packages rather than custom compilation or specific version requirements
- The target environment has internet access for package installation and Git repository cloning
- Current Chef Solo execution model suggests single-node deployments rather than multi-node orchestration
- UFW firewall rules assume standard port usage (22/SSH, 80/HTTP, 443/HTTPS) without custom port requirements
- Redis and Memcached services will run on default ports without clustering or replication requirements
- The "cluster.local" domain suffix suggests internal/private network deployment rather than public internet exposure