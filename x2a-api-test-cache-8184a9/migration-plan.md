# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database credentials in environment files
- **SSL Certificate Management**: Self-signed certificate generation for development environments needs migration to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban Integration**: Jail configuration for nginx protection
- **Sysctl Security**: Kernel parameter tuning for security hardening

### Technical Challenges

- **Redis Configuration Patching**: Complex ruby block that modifies Redis config file post-installation requires custom Ansible lineinfile tasks
- **Multi-site SSL Setup**: Dynamic certificate generation and nginx virtual host configuration based on node attributes
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment
- **Service Dependencies**: Proper ordering of PostgreSQL → application → nginx service startup
- **Template Migration**: Converting ERB templates to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations

### Migration Order

1. **cache** (low risk, standalone service)
   - Migrate memcached and Redis installation
   - Convert configuration patching logic
   - Test caching functionality independently

2. **nginx-multisite** (moderate complexity, security-focused)
   - Migrate security hardening components first
   - Convert SSL certificate generation
   - Implement multi-site virtual host configuration
   - Test firewall and fail2ban integration

3. **fastapi-tutorial** (high complexity, database dependencies)
   - Migrate PostgreSQL setup and user creation
   - Convert Python application deployment
   - Implement systemd service management
   - Test end-to-end application functionality

### Assumptions

- **Development Environment**: Self-signed certificates suggest this is primarily for development/testing rather than production
- **Single-Node Deployment**: No clustering or high-availability configurations detected
- **Local Database**: PostgreSQL is installed locally rather than using external database services
- **Static Site Content**: HTML files are deployed as static content rather than dynamic generation
- **Ubuntu/Debian Focus**: Package management and service names suggest primary target is Debian-based systems
- **Root Execution**: Many operations assume root privileges without sudo configuration
- **Network Isolation**: UFW rules suggest services are expected to be internet-facing
- **Manual Certificate Management**: No automated certificate renewal (Let's Encrypt) detected