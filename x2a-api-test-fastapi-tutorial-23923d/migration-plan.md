# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure setup for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and firewall rules. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx web server with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer services providing both in-memory (memcached) and persistent (Redis) caching with authentication and custom configuration management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service integration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef node attributes configuration defining nginx sites, SSL paths, and security settings for the target environment
- `solo.rb`: Chef Solo configuration specifying cookbook paths, cache location, and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated provisioning script handling Chef installation, Berkshelf dependency resolution, and cookbook execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata.rb files), with primary development/testing on Fedora 42 (from Vagrantfile)
- **Virtual Machine Technology**: libvirt/KVM (configured in Vagrantfile with 2GB RAM, 2 CPUs)
- **Cloud Platform**: Not specified - appears to be on-premises or local development focused

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management
- **Chef Berkshelf**: Replace with Ansible Galaxy for role dependency management
- **Chef Solo**: Replace with ansible-playbook execution

### Security Considerations
- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands needs conversion to community.crypto.openssl_* modules with proper certificate validation and renewal strategies
- **Firewall Configuration**: UFW commands need conversion to community.general.ufw module with proper rule ordering and state management
- **SSH Hardening**: Direct file manipulation of /etc/ssh/sshd_config needs conversion to ansible.posix.sshd_config module for safer configuration management
- **Vault/secrets management**: 
  - **nginx-multisite**: No hardcoded credentials detected, uses file-based SSL certificates
  - **cache**: 1 hardcoded credential detected - Redis password 'redis_secure_password_123' in recipes/default.rb
  - **fastapi-tutorial**: 2 hardcoded credentials detected - PostgreSQL password 'fastapi_password' and database connection string in .env file
  - **Total**: 3 credentials requiring Ansible Vault migration

### Technical Challenges
- **Custom Chef Resource Migration**: The lineinfile.rb custom resource needs conversion to ansible.builtin.lineinfile module with equivalent functionality for file manipulation
- **Ruby Block Logic**: Complex Ruby blocks in cache cookbook for Redis configuration cleanup need conversion to Ansible tasks using ansible.builtin.replace or ansible.builtin.blockinfile modules
- **Service Dependencies**: PostgreSQL service dependency in fastapi-tutorial needs proper Ansible handler and dependency management
- **Template Variable Mapping**: ERB templates need conversion to Jinja2 with variable name mapping from Chef node attributes to Ansible variables
- **Git Repository Management**: Chef git resource needs conversion to ansible.builtin.git module with proper authentication and version control

### Migration Order
1. **cache** (low risk, minimal dependencies, straightforward service installation)
2. **fastapi-tutorial** (moderate complexity, database setup, but isolated functionality)
3. **nginx-multisite** (high complexity, security configurations, SSL management, depends on other services being available for testing)

### Assumptions
- Target environments will maintain the same OS distributions (Ubuntu 18.04+, CentOS 7+) as specified in Chef cookbook metadata
- Self-signed certificates are acceptable for development environments; production environments will require proper CA-signed certificates or Let's Encrypt integration
- Current hardcoded passwords in cache and fastapi-tutorial cookbooks are development/testing credentials and will be replaced with Ansible Vault-managed secrets
- The libvirt/KVM virtualization platform will be maintained for development environments
- Network configuration (192.168.121.10, port forwarding) requirements will remain consistent
- PostgreSQL database will be co-located on the same server as the FastAPI application (not using external database service)
- Redis and Memcached services will run on default ports without clustering requirements
- The GitHub repository for FastAPI tutorial (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the 'main' branch will be used
- UFW firewall rules are sufficient for the security requirements (no iptables or other firewall solutions needed)
- Systemd is available on target systems for service management (standard on Ubuntu 18.04+ and CentOS 7+)
- The custom lineinfile resource functionality is only used for simple file modifications that can be replaced with standard Ansible modules