# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and system hardening. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), SSH hardening, and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall with HTTP/HTTPS/SSH rules, SSH root login disable, password authentication disable, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer configuration with Memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service via external cookbook, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment, Git repository cloning from GitHub (dibanez/fastapi_tutorial), PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef node configuration with run_list, nginx site definitions, SSL paths, and security settings (fail2ban, UFW, SSH hardening)
- `solo.rb`: Chef Solo configuration specifying cookbook paths, cache location, and logging
- `Vagrantfile`: Development environment using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder sync
- `vagrant-provision.sh`: Automated provisioning script installing Chef, Berkshelf, downloading dependencies, and running Chef Solo

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible-role-nginx or community.general.nginx modules
- **memcached (~> 6.0)**: Replace with ansible-memcached role or package/service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or geerlingguy.redis role
- **Chef Berkshelf**: Replace with ansible-galaxy for role dependency management
- **Chef Solo**: Replace with ansible-playbook execution

### Security Considerations
- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands needs conversion to ansible.builtin.openssl_* modules or community.crypto collection
- **Firewall Configuration**: UFW commands need conversion to community.general.ufw module
- **SSH Hardening**: Direct file editing of /etc/ssh/sshd_config needs conversion to ansible.posix.sshd_config or lineinfile modules
- **Fail2ban Configuration**: Template-based jail.local configuration needs conversion to community.general.fail2ban module
- **Vault/secrets management**: 
  - **nginx-multisite**: No hardcoded credentials detected, SSL certificates are self-generated
  - **cache**: 1 hardcoded Redis password ('redis_secure_password_123') in default recipe - needs Ansible Vault encryption
  - **fastapi-tutorial**: 2 hardcoded credentials detected - PostgreSQL password ('fastapi_password') and database connection string in .env file - both need Ansible Vault encryption
  - **Total credentials requiring vault migration**: 3 credential instances across 2 modules

### Technical Challenges
- **Custom Chef Resource**: The lineinfile.rb custom resource needs conversion to ansible.builtin.lineinfile module with equivalent functionality
- **Ruby Block Logic**: Complex Ruby logic in cache cookbook for Redis configuration cleanup needs conversion to Ansible tasks with conditional logic
- **Template Variables**: ERB templates need conversion to Jinja2 format with variable mapping
- **Service Dependencies**: PostgreSQL service dependency in FastAPI cookbook needs proper Ansible handler and dependency management
- **Git Repository Cloning**: Chef git resource needs conversion to ansible.builtin.git module with equivalent revision tracking
- **Systemd Service Management**: File-based systemd service creation needs conversion to ansible.builtin.systemd module

### Migration Order
1. **cache** (low risk, minimal dependencies, straightforward service configuration)
2. **fastapi-tutorial** (moderate complexity, database dependencies, but isolated application)
3. **nginx-multisite** (high complexity, multiple security components, custom resources, affects other services)

### Assumptions
- Target environment will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development; production will require proper CA-signed certificates or Let's Encrypt integration
- Current hardcoded passwords in cache and fastapi-tutorial cookbooks are development placeholders and will be replaced with Ansible Vault encrypted variables
- The custom lineinfile resource functionality can be fully replicated with Ansible's built-in lineinfile module
- PostgreSQL database initialization and user creation can be handled by community.postgresql collection
- The Ruby block logic for Redis configuration cleanup indicates potential issues with the redisio cookbook that may not exist in Ansible Redis roles
- Vagrant development environment will be replaced with equivalent Ansible testing setup (molecule, vagrant, or container-based testing)
- Network configuration (192.168.121.10, port forwarding) suggests development/testing environment that may need adjustment for production deployment
- The GitHub repository (dibanez/fastapi_tutorial) referenced in fastapi-tutorial cookbook is accessible and will remain available during migration
- Current Chef Solo execution model will be replaced with Ansible playbook execution, requiring inventory management setup
- Berkshelf vendor directory management will be replaced with ansible-galaxy role installation and requirements.yml management