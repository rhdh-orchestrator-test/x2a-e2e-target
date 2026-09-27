# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching services, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW firewall, and SSH hardening
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH security (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services layer providing both memcached and Redis with authentication and custom configuration
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, Redis log directory management, configuration file patching for Redis compatibility

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template for redis.conf, and ansible.builtin.service modules

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths are configured but certificate provisioning method unclear - need to establish certificate deployment strategy
- **SSH hardening**: Root login disabled and password authentication disabled - preserve these security settings in Ansible
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Intrusion prevention via fail2ban.jail.local template - migrate to ansible.builtin.template
- **Sysctl security tuning**: Kernel parameter hardening via sysctl - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis config file post-installation - need to replace with proper Ansible template or lineinfile modules
- **PostgreSQL database initialization**: Database and user creation uses shell commands with sudo - migrate to ansible.builtin.postgresql_db and ansible.builtin.postgresql_user modules
- **Git repository management**: FastAPI app cloning uses Chef git resource - migrate to ansible.builtin.git module
- **Systemd service creation**: Custom systemd service file creation - migrate to ansible.builtin.template and ansible.builtin.systemd modules
- **Multi-site nginx configuration**: Dynamic site creation based on node attributes - migrate to Ansible loops with ansible.builtin.template

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on SSL certificate strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- SSL certificates are manually deployed or obtained via external process (certificate provisioning method not defined in cookbooks)
- Target environment has internet access for package installation and git repository cloning
- PostgreSQL service is managed by system package manager (not containerized)
- Redis and memcached run as system services (not containerized)
- UFW firewall is the preferred firewall solution (no iptables rules defined)
- Development/testing uses Vagrant but production deployment method is undefined
- Node attributes in solo.json represent production configuration values
- External cookbook dependencies (nginx, memcached, redisio) provide standard service installation and basic configuration only