# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis configuration cleanup via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Vagrant configuration for local development environment provisioning
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module

### Security Considerations

- **Hardcoded credentials**: Redis password and PostgreSQL credentials are embedded in recipe files - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths are configured but certificate provisioning method unclear - needs certificate deployment strategy
- **SSH security hardening**: Root login disable and password authentication disable configurations need careful testing
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS) requires validation
- **Fail2ban configuration**: Custom jail.local template needs conversion to Ansible template
- **Database credentials**: PostgreSQL user creation with hardcoded password needs Vault integration

### Technical Challenges

- **Redis configuration cleanup**: Chef ruby_block performing regex-based config file manipulation needs conversion to Ansible lineinfile or template approach
- **Multi-site SSL configuration**: Complex nginx virtual host templating with SSL per subdomain requires careful Ansible template conversion
- **Service dependencies**: PostgreSQL must be running before FastAPI application deployment - requires proper task ordering and handlers
- **Git repository management**: FastAPI tutorial cloning and virtual environment setup needs idempotent Ansible git and pip modules
- **Systemd service creation**: Custom systemd unit file creation and daemon-reload coordination requires proper Ansible handlers

### Migration Order

1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **nginx-multisite** (moderate complexity, security configurations require careful testing)
3. **fastapi-tutorial** (high complexity, database dependencies and application deployment coordination)

### Assumptions

- SSL certificates are manually managed or provided externally (no automated certificate provisioning detected in cookbooks)
- Development environment uses Vagrant but production deployment method is unspecified
- Database backup and recovery procedures are not defined in current Chef configuration
- Log rotation and monitoring configurations are not present in current cookbooks
- Network security groups or external firewall rules are managed outside of these cookbooks
- The FastAPI tutorial application source code repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Redis and PostgreSQL data persistence requirements are not explicitly defined in current configuration