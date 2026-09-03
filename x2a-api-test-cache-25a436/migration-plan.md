# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and firewall rules. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion detection, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer configuration with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service setup, Redis 6379 with password authentication, custom Redis configuration cleanup via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef node attributes defining nginx site configurations, SSL paths, and security settings for the target environment
- `solo.rb`: Chef Solo configuration specifying cookbook paths, cache location, and logging settings
- `Vagrantfile`: Development environment configuration using Fedora 42 with libvirt provider, network setup (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated provisioning script for Chef installation, Berkshelf dependency resolution, and cookbook execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Primary target appears to be Ubuntu based on package management patterns in recipes.
- **Virtual Machine Technology**: KVM/libvirt (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment based on private network configuration (192.168.121.0/24)

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible-role-nginx or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **Chef Supermarket cookbooks**: All external dependencies need Ansible Galaxy role equivalents or custom implementation

### Security Considerations
- SSL certificate management: Self-signed certificate generation for development environments requires OpenSSL command tasks in Ansible
- Firewall configuration: UFW rules (SSH, HTTP, HTTPS) need ufw module or firewalld equivalent
- SSH hardening: Root login disable and password authentication disable require lineinfile tasks
- Fail2ban configuration: Custom jail.local template needs conversion to Ansible template
- Sysctl security tuning: Security parameters in /etc/sysctl.d/99-security.conf require sysctl module
- Vault/secrets management: For each module, credential patterns identified:
  - **nginx-multisite**: SSL private keys, certificate files (3 sites × 2 files = 6 sensitive files)
  - **cache**: Redis password 'redis_secure_password_123' hardcoded in recipe (1 credential)
  - **fastapi-tutorial**: PostgreSQL password 'fastapi_password' hardcoded in recipe, DATABASE_URL in .env file (2 credentials)
  - **Total**: 9 credentials requiring Ansible Vault management

### Technical Challenges
- Custom Chef resources: The lineinfile.rb custom resource needs conversion to Ansible lineinfile module
- Ruby blocks: Complex Ruby logic in cache cookbook for Redis configuration cleanup requires equivalent shell/command tasks
- Template variables: ERB templates need conversion to Jinja2 format with variable mapping
- Service dependencies: PostgreSQL service dependency in fastapi-tutorial requires proper task ordering and handlers
- File permissions: SSL certificate group ownership (ssl-cert) and directory permissions need careful mapping
- Git repository cloning: FastAPI tutorial Git clone with revision tracking needs ansible.builtin.git module

### Migration Order
1. **cache** (low risk, minimal dependencies, straightforward service configuration)
2. **fastapi-tutorial** (moderate complexity, database setup, but isolated application)
3. **nginx-multisite** (high complexity, multiple dependencies, security configurations, custom resources)

### Assumptions
- Target systems will have internet access for package installation and Git repository cloning
- PostgreSQL installation and configuration patterns are consistent across target environments
- SSL certificate requirements remain self-signed for development (production may need Let's Encrypt or CA-signed certificates)
- UFW firewall is acceptable on target systems (may need firewalld for RHEL/CentOS environments)
- Python 3 virtual environment approach is preferred over system-wide package installation
- Redis authentication requirements remain consistent with current password-based approach
- Systemd is available on target systems for service management
- The GitHub repository https://github.com/dibanez/fastapi_tutorial.git remains accessible and stable
- Current hardcoded passwords are acceptable for development environments (production will require Ansible Vault)
- Network configuration (192.168.121.0/24) is specific to development and will need adjustment for production environments
- Chef cookbook external dependencies (nginx, memcached, redisio) have suitable Ansible equivalents available
- File synchronization approach in Vagrant (rsync) may need adjustment for production deployment methods
- The Fedora 42 development environment translates appropriately to Ubuntu/CentOS production targets