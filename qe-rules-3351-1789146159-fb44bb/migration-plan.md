# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, including custom Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication (password: redis_secure_password_123), Memcached integration, custom Redis config patching, log directory creation

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment file management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks from Chef Supermarket
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script
- `x2a-rules/`: Contains migration rule files (65ce94b0-f8d3-41f5-8026-8413038d1c00.md)

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata), recommend standardizing on Red Hat Enterprise Linux 9 for production
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified in current configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis modules and custom configuration tasks

### Security Considerations

- **Hardcoded Credentials**: 
  - Redis password (redis_secure_password_123) hardcoded in cache cookbook - migrate to Ansible Vault
  - PostgreSQL password (fastapi_password) hardcoded in fastapi-tutorial cookbook - migrate to Ansible Vault
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve in Ansible configuration
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.firewalld or ufw modules
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate using community.general.fail2ban modules
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate using ansible.posix.sysctl module

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules
- **Multi-site SSL Certificate Generation**: Complex logic for generating per-site SSL certificates with proper permissions and ownership - requires careful Ansible task sequencing
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering and health checks in Ansible
- **Template Variable Mapping**: Chef ERB templates need conversion to Jinja2 with proper variable scoping and attribute mapping

### Migration Order

1. **cache** (Priority 1: Standalone caching services, moderate complexity due to custom Redis config patching)
2. **nginx-multisite** (Priority 2: Complex security and SSL configuration, but well-isolated functionality)
3. **fastapi-tutorial** (Priority 3: Application deployment with database dependencies, highest integration complexity)

### Assumptions

- Current Chef cookbooks are used with Chef Solo (based on solo.json/solo.rb presence) rather than Chef Server
- Development environment uses Vagrant for testing (Vagrantfile present)
- Production deployment targets are Ubuntu/CentOS as specified in metadata
- SSL certificates are currently self-signed for development/testing purposes
- Database credentials and Redis passwords will be externalized to Ansible Vault during migration
- The x2a-rules directory contains existing migration documentation or rules that should be referenced
- Current firewall rules (UFW) are appropriate for the target environment
- PostgreSQL version compatibility is maintained between Chef and Ansible deployments
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible