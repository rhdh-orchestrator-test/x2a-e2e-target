# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file post-processing via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Vagrant provisioning script for Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic infrastructure

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management via systemd
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module and virtual environment management

### Security Considerations

- **Hardcoded credentials**: Redis password and PostgreSQL credentials are embedded in recipes and need migration to Ansible Vault
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi:fastapi_password` in fastapi-tutorial cookbook
- **SSL certificate management**: Certificate paths are configured but certificate provisioning method unclear - needs investigation
- **SSH hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW configuration with specific port allowances (22, 80, 443) requires ufw module or firewalld equivalent
- **Fail2ban configuration**: Intrusion prevention rules need migration to appropriate Ansible modules

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains Ruby code blocks for Redis configuration file manipulation that need conversion to Ansible file manipulation modules
- **Multi-site nginx configuration**: Complex template-driven virtual host configuration requires careful Ansible template conversion
- **Service dependencies**: PostgreSQL must be running before FastAPI application setup, requiring proper task ordering in Ansible
- **Git repository management**: FastAPI cookbook clones external repository which needs conversion to ansible.builtin.git module
- **Custom resource usage**: nginx-multisite uses custom `lineinfile` resource that needs mapping to ansible.builtin.lineinfile

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached setup with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- SSL certificates are managed externally or via Let's Encrypt (certificate provisioning method not visible in current cookbooks)
- The FastAPI tutorial repository at `https://github.com/dibanez/fastapi_tutorial.git` remains accessible and stable
- Current Chef external cookbook versions (nginx 12.0, memcached 6.0, redisio 7.2.4) provide compatible functionality with target Ansible modules
- Target systems have internet access for package installation and git repository cloning
- PostgreSQL installation method (package vs. container vs. external service) needs clarification as cookbook only shows basic package installation
- UFW firewall is the preferred firewall solution (vs. firewalld on RHEL systems)
- The Ruby block configuration fixes in the cache cookbook address specific Redis version compatibility issues that may not be needed with newer Redis versions or different configuration approaches