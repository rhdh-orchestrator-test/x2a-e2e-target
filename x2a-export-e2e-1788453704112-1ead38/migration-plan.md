# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and hardened system settings. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **cache**:
    - Description: Caching services configuration with memcached and Redis 6379 with authentication, custom log directory setup, and configuration file patching for Redis compatibility
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication (redis_secure_password_123), memcached service, Redis log directory management, configuration file manipulation via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, systemd service management, and Git-based source deployment
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment, PostgreSQL database creation, systemd service configuration, Git repository cloning from GitHub, environment file management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, self-signed certificate generation, and custom resource for file line management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL sites (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security settings, custom lineinfile resource

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder synchronization
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency management script for Vagrant provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: KVM/libvirt (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo**: Replace with Ansible playbooks and inventory management
- **Berkshelf**: Replace with Ansible Galaxy and requirements.yml for external role dependencies

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires Ansible Vault encryption
- **PostgreSQL credentials**: FastAPI database password "fastapi_password" needs secure variable management
- **SSL certificate management**: Self-signed certificate generation logic needs conversion to ansible.builtin.openssl_* modules
- **SSH hardening**: Root login disable and password authentication disable configurations need careful testing
- **Firewall rules**: UFW commands need conversion to community.general.ufw module with proper rule ordering
- **Vault/secrets management**: 
  - cache module: 1 Redis password credential detected
  - fastapi-tutorial module: 1 PostgreSQL password credential detected
  - nginx-multisite module: SSL certificate paths and security configurations (no hardcoded secrets)
  - Total: 2 credentials requiring Ansible Vault management

### Technical Challenges
- **Custom Chef resource migration**: The lineinfile.rb custom resource needs conversion to ansible.builtin.lineinfile module with equivalent functionality
- **Ruby block logic**: Complex file manipulation in cache cookbook (Redis config patching) requires conversion to Ansible template or lineinfile tasks
- **Service dependencies**: PostgreSQL service must be running before database creation in fastapi-tutorial cookbook
- **Template conversion**: All ERB templates (.erb files) need conversion to Jinja2 format for Ansible
- **Attribute precedence**: Chef node attributes and solo.json overrides need mapping to Ansible variable precedence
- **Git repository handling**: FastAPI tutorial Git cloning needs conversion to ansible.builtin.git module with proper change detection

### Migration Order
1. **cache** (low risk, standalone service, clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies, systemd service)
3. **nginx-multisite** (high complexity, multiple sites, security configurations, custom resources)

### Assumptions
- Target environment will use systemd for service management (based on fastapi-tutorial systemd service configuration)
- SSL certificates will remain self-signed for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis will be installed on the same host as the applications (no external database servers assumed)
- UFW firewall is acceptable for the target environment (may need iptables conversion for some distributions)
- The Git repository https://github.com/dibanez/fastapi_tutorial.git will remain accessible during migration
- Vagrant development environment will be replaced with Ansible-based local testing (molecule or direct playbook execution)
- Chef Supermarket cookbooks (nginx, memcached, redisio) functionality will be replicated using Ansible built-in modules rather than external Galaxy roles
- File permissions and ownership patterns from Chef cookbooks will be preserved in Ansible tasks
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the production site structure
- Network configuration (192.168.121.10 IP address) is development-specific and will need environment-specific variable management