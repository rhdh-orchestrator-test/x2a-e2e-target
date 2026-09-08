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
    - Key Features: Git repository cloning, Python venv setup, PostgreSQL database and user creation, systemd service management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations
- SSH hardening configurations: Root login disabled, password authentication disabled
- Firewall management: UFW rules for SSH (22), HTTP (80), HTTPS (443)
- Fail2ban integration: Custom jail configuration for nginx protection
- SSL certificate management: Self-signed certificate generation for development environments
- Sysctl security tuning: Custom kernel parameter hardening
- Credential patterns identified:
  - Redis password: Hardcoded in cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials: Hardcoded in fastapi-tutorial cookbook (`fastapi_password`)
  - SSL certificate generation: Self-signed certificates with embedded organization details

### Technical Challenges
- **Custom Redis Configuration Patching**: The cache cookbook uses ruby_block to manually edit Redis config files, removing specific configuration lines - this will need to be replaced with proper template management in Ansible
- **Multi-site SSL Certificate Management**: Complex logic for generating and managing SSL certificates per site with proper file permissions and group ownership
- **Service Interdependencies**: FastAPI service depends on PostgreSQL being ready, nginx depends on SSL certificates being generated
- **File Permission Management**: Complex ownership patterns (www-data, ssl-cert group) that need careful translation to Ansible

### Migration Order
1. **cache** (low risk, moderate complexity) - Straightforward service installation with known credential management needs
2. **fastapi-tutorial** (moderate complexity) - Database setup and application deployment with clear service dependencies
3. **nginx-multisite** (high complexity) - Complex multi-site configuration with SSL, security hardening, and firewall rules

### Assumptions
- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require different certificate management)
- The custom Redis configuration patching approach indicates potential compatibility issues that may need investigation
- Hardcoded passwords suggest this is a development/testing environment - production deployment will require proper secret management
- The Vagrant-based development workflow suggests the team is familiar with infrastructure-as-code practices
- External cookbook dependencies (nginx, memcached, redisio) functionality will need to be replicated using Ansible modules or custom tasks
- The multi-site nginx configuration pattern suggests a microservices or multi-tenant architecture that should be preserved in the Ansible migration