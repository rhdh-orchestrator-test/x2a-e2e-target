# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef Solo configuration that provisions a multi-site nginx web server with SSL termination, caching services (Redis and Memcached), and a FastAPI tutorial application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, UFW, SSH hardening), custom lineinfile resource, ERB templates for nginx.conf and site configurations

- **cache**:
    - Description: Caching layer configuration with Memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached service, custom Redis configuration patching via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list and node attributes including nginx site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder sync
- `vagrant-provision.sh`: Automated provisioning script installing Chef, Berkshelf, and running cookbook dependencies

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for standardization.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **berkshelf**: Replace with ansible-galaxy for role dependencies
- **chef-solo**: Replace with ansible-playbook execution

### Security Considerations
- **Hardcoded credentials**: Redis password 'redis_secure_password_123' in cache/recipes/default.rb needs vault management
- **PostgreSQL credentials**: FastAPI database password 'fastapi_password' in fastapi-tutorial/recipes/default.rb requires secure storage
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH hardening**: Root login disable and password authentication disable configurations need migration
- **Firewall rules**: UFW configuration for ports 22, 80, 443 needs migration to ansible.posix.ufw module
- **Fail2ban configuration**: Jail configuration template needs migration to Ansible template module
- **Vault/secrets management**: 2 hardcoded passwords detected requiring Ansible Vault integration

### Technical Challenges
- **Custom Ruby resource**: The lineinfile.rb custom resource needs migration to ansible.builtin.lineinfile module with equivalent functionality
- **Ruby block hacks**: Redis configuration patching via ruby_block in cache cookbook requires custom Ansible tasks or template-based approach
- **Template migration**: 5 ERB templates need conversion to Jinja2 format (nginx.conf.erb, site.conf.erb, security.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb)
- **Berkshelf vendor process**: Cookbook dependency resolution needs migration to Ansible Galaxy role dependencies
- **Chef Solo attributes**: Node attribute hierarchy and precedence needs mapping to Ansible variable precedence
- **Service notification**: Chef's delayed notifications need migration to Ansible handlers

### Migration Order
1. **cache cookbook** (low risk, foundational service) - Memcached and Redis setup with basic configuration
2. **fastapi-tutorial cookbook** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite cookbook** (high complexity, multiple dependencies) - Web server with SSL, security, and multi-site configuration

### Assumptions
- Target environment will maintain the same network configuration (192.168.121.10 private network)
- SSL certificate requirements will remain self-signed for development (production may need Let's Encrypt integration)
- PostgreSQL and Redis authentication requirements will be maintained with secure credential storage
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved
- Systemd service management is available on target systems
- UFW firewall is acceptable for the target environment (may need iptables alternative for RHEL)
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- Python 3 virtual environment approach will be maintained for application isolation
- Current Chef cookbook supports (Ubuntu 18.04+, CentOS 7+) indicate target OS compatibility requirements
- Development workflow using Vagrant will be replaced with Ansible testing methodology
- The custom lineinfile resource functionality is required and needs equivalent Ansible implementation