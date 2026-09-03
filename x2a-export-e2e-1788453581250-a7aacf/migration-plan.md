# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSH hardening.

**Migration Complexity**: Medium-High (3 cookbooks, external dependencies, security configurations, SSL management)
**Estimated Timeline**: 3-4 weeks (1 week per cookbook + 1 week for integration testing and documentation)
**Team Coordination**: Requires coordination between web infrastructure, security, and application teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, includes Redis log directory management and configuration file patching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication (redis_secure_password_123), Memcached integration, Redis configuration file post-processing, custom log directory setup

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service management, environment configuration file

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban integration, UFW firewall management, SSH hardening, self-signed certificate generation, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node attributes and run list configuration - contains site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration - defines cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding for HTTP/HTTPS
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution using Berkshelf

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). The Vagrantfile uses Fedora 42 for development, but production targets are Ubuntu/CentOS.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Berkshelf**: Replace with Ansible Galaxy for role dependency management
- **Chef Solo**: Replace with ansible-playbook execution

### Security Considerations

- **Hardcoded Redis Password**: The cache cookbook contains hardcoded Redis password 'redis_secure_password_123' in recipes/default.rb - migrate to Ansible Vault
- **PostgreSQL Credentials**: FastAPI cookbook has hardcoded database password 'fastapi_password' - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security settings in Ansible
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Sysctl Security Settings**: Kernel parameter hardening via /etc/sysctl.d/99-security.conf template

**Vault/secrets management**: 
- **cache module**: 1 Redis password credential detected
- **fastapi-tutorial module**: 2 credentials detected (PostgreSQL user password, database connection string)
- **nginx-multisite module**: SSL certificate generation (3 self-signed certificates for subdomains)
- **Total credentials**: 6 secrets requiring Ansible Vault management

### Technical Challenges

- **Custom Chef Resource Migration**: The nginx-multisite cookbook includes a custom 'lineinfile' resource (resources/lineinfile.rb) that needs to be replaced with ansible.builtin.lineinfile module
- **Redis Configuration Patching**: The cache cookbook uses a Ruby block to post-process Redis configuration files by removing specific lines - this complex logic needs careful translation to Ansible tasks
- **Template Migration**: 5 ERB templates in nginx-multisite need conversion to Jinja2 format (nginx.conf.erb, site.conf.erb, fail2ban.jail.local.erb, security.conf.erb, sysctl-security.conf.erb)
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple subdomains requires careful loop handling in Ansible
- **Git Repository Integration**: FastAPI cookbook clones from GitHub - ensure proper git module usage and repository access
- **Service Dependencies**: Complex service startup order (PostgreSQL before FastAPI, nginx after SSL certificates) requires proper Ansible handlers and dependencies

### Migration Order

1. **cache cookbook** (Priority 1: Low risk, standalone caching services)
   - Migrate Redis and Memcached installation
   - Address hardcoded password with Ansible Vault
   - Test caching service functionality

2. **fastapi-tutorial cookbook** (Priority 2: Moderate complexity, database dependencies)
   - Migrate Python application deployment
   - Convert PostgreSQL setup and user management
   - Implement systemd service configuration
   - Secure database credentials with Vault

3. **nginx-multisite cookbook** (Priority 3: High complexity, security and SSL dependencies)
   - Convert custom lineinfile resource usage
   - Migrate security hardening (fail2ban, UFW, SSH)
   - Implement multi-site SSL certificate management
   - Convert all ERB templates to Jinja2
   - Integrate with previously migrated services

### Assumptions

- **Target Environment**: Assuming Ubuntu/CentOS production deployment despite Fedora development environment
- **Network Configuration**: Assuming private network 192.168.121.0/24 based on Vagrantfile, may need adjustment for production
- **SSL Strategy**: Assuming self-signed certificates are acceptable for development; production may require proper CA-signed certificates or Let's Encrypt integration
- **Database Location**: Assuming PostgreSQL will be co-located on the same server as the FastAPI application
- **Service User**: Assuming services will run as root user as configured in Chef recipes; may need to implement proper service users for security
- **Package Managers**: Assuming apt (Ubuntu/Debian) and yum/dnf (CentOS/RHEL) package managers based on cookbook supports declarations
- **Firewall Management**: Assuming UFW is the preferred firewall solution; iptables may be required for CentOS environments
- **Git Access**: Assuming public GitHub repository access for FastAPI tutorial; private repositories would require SSH key or token management
- **Chef License**: Current setup uses Chef with accepted license; Ansible eliminates licensing concerns
- **Development Workflow**: Assuming Vagrant development environment will be replaced with Ansible testing framework (molecule or similar)