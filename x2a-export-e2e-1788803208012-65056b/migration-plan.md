# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching services, a FastAPI application, and an nginx reverse proxy with SSL termination. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration managing both memcached and Redis with authentication, custom log directories, and configuration fixes for Redis compatibility
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-domain hosting, security hardening via fail2ban and UFW firewall, and SSH security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes and need to be moved to Ansible Vault
- **SSL certificate management**: SSL certificate paths are configured but certificate provisioning method is not defined in the current cookbooks
- **SSH security hardening**: Root login disabled, password authentication disabled - these configurations need careful migration to avoid lockout
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH need to be replicated with ansible.posix.ufw module
- **Fail2ban configuration**: Custom jail.local template needs migration to Ansible template management
- **Sysctl security tuning**: Security kernel parameters configured via template need migration

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually patches Redis configuration files to remove incompatible directives - this logic needs to be reimplemented in Ansible
- **PostgreSQL database initialization**: Database and user creation commands use shell execution with error handling ("|| true") that needs proper Ansible idempotency
- **Multi-domain nginx configuration**: Template-driven site configuration for multiple SSL domains requires careful migration of ERB templates to Jinja2
- **Service dependency management**: FastAPI service depends on PostgreSQL being available, requiring proper Ansible handler and dependency ordering

### Migration Order

1. **cache** (moderate complexity, standalone service, good starting point for Redis/memcached patterns)
2. **nginx-multisite** (moderate complexity, security-critical, establishes web infrastructure foundation)
3. **fastapi-tutorial** (highest complexity, depends on database setup, application-specific configuration)

### Assumptions

- SSL certificates are managed externally or through a separate process not defined in these cookbooks
- The development environment uses Vagrant but production deployment method is not specified
- Database backup and recovery procedures are not defined in the current configuration
- Log rotation and monitoring configurations are not present in the current cookbooks
- The "cluster.local" domain names suggest a local development or testing environment rather than production
- Network security beyond UFW firewall rules (such as network segmentation) is handled at the infrastructure level
- The Redis configuration patching suggests compatibility issues with the redisio cookbook that may not exist with native Ansible Redis management