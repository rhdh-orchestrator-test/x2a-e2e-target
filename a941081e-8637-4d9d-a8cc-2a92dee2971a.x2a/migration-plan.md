# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration managing a multi-site nginx web server with SSL termination, security hardening, caching services (Redis and Memcached), and a FastAPI application backed by PostgreSQL. The migration to Ansible is straightforward with low-to-moderate complexity, estimated at 2-3 weeks for a team of 2-3 engineers including testing and validation.

## Module Migration Plan

This repository contains 3 Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configured for hosting multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) with comprehensive security hardening including fail2ban, UFW firewall, SSH hardening, and kernel security parameters via sysctl
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificate generation, HTTP to HTTPS redirects, TLS 1.2/1.3 with strong cipher suites, HSTS headers, security headers (X-Frame-Options, X-Content-Type-Options, CSP), gzip compression, fail2ban intrusion prevention, UFW firewall with default-deny policy, SSH root login disabled, SSH password authentication disabled, sysctl kernel hardening

- **cache**:
    - Description: Caching layer services providing both Memcached and Redis with authentication, configured for high-performance data caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service installation and configuration, Redis 6379 with requirepass authentication (password: redis_secure_password_123), custom Redis log directory setup, config file post-processing to remove deprecated replica directives

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, including git-based code deployment, Python virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 with venv and pip, git repository cloning from https://github.com/dibanez/fastapi_tutorial.git, PostgreSQL database and user provisioning (database: fastapi_db, user: fastapi, password: fastapi_password), environment variable configuration via .env file, systemd service for uvicorn ASGI server on port 8000, automatic service restart on failure

### Infrastructure Files

- **Berksfile**: Chef Berkshelf dependency management declaring external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbooks; migrate to Ansible Galaxy requirements.yml or ansible-galaxy install commands
- **solo.json**: Chef Solo node attributes defining run list and site-specific configuration including SSL paths, security settings, and virtual host definitions; migrate to Ansible inventory variables and group_vars
- **solo.rb**: Chef Solo configuration specifying cookbook paths and logging; no Ansible equivalent needed (replaced by ansible.cfg)
- **Vagrantfile**: Development VM configuration using Fedora 42 with libvirt provider, 2GB RAM, 2 CPUs, and port forwarding for HTTP/HTTPS; can be preserved with Ansible provisioner or migrated to Vagrant shell provisioner calling ansible-playbook
- **vagrant-provision.sh**: Shell script for installing Chef, Berkshelf, and running chef-solo; replace with equivalent script installing Ansible and running ansible-playbook
- **cookbooks/nginx-multisite/templates/**: ERB templates for nginx.conf, site.conf, security.conf, fail2ban.jail.local, and sysctl-security.conf; migrate to Jinja2 templates with similar variable substitution
- **cookbooks/nginx-multisite/files/default/**: Static HTML files for test, ci, and status sites; migrate directly to Ansible files/ directory with identical structure
- **cookbooks/nginx-multisite/resources/lineinfile.rb**: Custom Chef resource for line-in-file operations; replace with Ansible's built-in lineinfile module

### Target Details

- **Operating System**: Ubuntu 18.04+ (primary), CentOS 7+ (secondary support); inferred from cookbook metadata.rb supports declarations and package names (apt-based packages like libpq-dev, www-data user/group)
- **Virtual Machine Technology**: Vagrant with libvirt provider (KVM/QEMU); specified in Vagrantfile with generic/fedora42 box for testing
- **Cloud Platform**: Not specified; local development and testing environment using private network (192.168.121.10)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Community cookbook from Chef Supermarket; replace with ansible.builtin.package and ansible.builtin.template modules, or use geerlingguy.nginx role from Ansible Galaxy (version 3.x+)
- **memcached (~> 6.0)**: Community cookbook for Memcached installation; replace with ansible.builtin.package module and geerlingguy.memcached role, or install directly via package manager
- **redisio (~> 7.2.4)**: Community cookbook for Redis installation and configuration; replace with geerlingguy.redis role from Ansible Galaxy or davidwittman.redis, including custom authentication configuration
- **Chef Infra Client and Berkshelf**: Development toolchain dependencies; eliminate entirely and replace with Ansible and ansible-galaxy

### Security Considerations

- **Hardcoded credentials in recipes and attributes**:
  - Redis password: `redis_secure_password_123` in cookbooks/cache/recipes/default.rb
  - PostgreSQL password: `fastapi_password` in cookbooks/fastapi-tutorial/recipes/default.rb
  - PostgreSQL connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db` in .env file
  - **Migration strategy**: Move all credentials to Ansible Vault encrypted variables; use ansible-vault encrypt_string for inline encryption or separate vault files per environment
  
- **Self-signed SSL certificates**: Generated dynamically via OpenSSL for development; consider Let's Encrypt integration using certbot Ansible role for production environments, or continue self-signed approach with ansible.builtin.openssl_certificate module

- **SSH hardening configurations**: Root login disabled, password authentication disabled via sed-based sshd_config modification; migrate to ansible.builtin.lineinfile or ansible.posix.sshd_config module for idempotent configuration

- **Firewall rules via UFW**: Default-deny policy with explicit SSH/HTTP/HTTPS allow rules executed via shell commands; replace with community.general.ufw module for declarative firewall management

- **Fail2ban intrusion prevention**: Template-based jail.local configuration for nginx protection; migrate template to Jinja2 and use community.general.fail2ban role or custom tasks

- **Kernel security parameters**: sysctl settings via template in /etc/sysctl.d/99-security.conf; migrate to ansible.posix.sysctl module for idempotent kernel parameter management

- **TLS/SSL configuration**: Strong cipher suites, TLS 1.2/1.3 only, HSTS headers; preserve identical configuration in Ansible-managed nginx templates

- **Security headers**: X-Frame-Options, X-Content-Type-Options, CSP, etc.; maintain same headers in migrated nginx site templates

- **Credential types identified across modules**:
  - Database credentials: PostgreSQL (1 instance)
  - Redis authentication: requirepass (1 instance)
  - SSL private keys: Per-site certificates (3 instances)
  - No evidence of Chef encrypted data bags or Chef Vault usage

### Technical Challenges

- **Ruby-based custom resources**: The lineinfile.rb custom resource provides functionality; Ansible's lineinfile module is a direct drop-in replacement with similar parameters (path, line, regexp)

- **Chef-specific configuration management patterns**: Delayed notifications (notifies :reload, :delayed) and immediate notifications; migrate to Ansible handlers for service restarts/reloads triggered by template/file changes

- **Berkshelf vendor workflow**: Chef uses Berkshelf to vendor external cookbooks into local cookbooks/ directory; Ansible Galaxy installs roles to ~/.ansible/roles or project-specific roles/ directory via requirements.yml

- **Node attribute precedence and merging**: Chef attributes have complex precedence (default, override, automatic); Ansible uses simpler variable precedence (defaults, vars, extra_vars) requiring careful review of attribute overrides in solo.json

- **Ruby ERB templates vs Jinja2**: Similar syntax but different filters and functions; most conversions are straightforward (<%= @var %> becomes {{ var }}), but complex Ruby logic in templates needs refactoring

- **Execute resources with guards**: Chef's not_if/only_if guards on execute resources; migrate to Ansible's changed_when, failed_when, and when conditional clauses, or use stat/command + register patterns

- **Git resource idempotency**: Chef git resource with :sync action; use ansible.builtin.git module with force=yes for similar behavior, or version parameter for specific commits

- **Systemd service management**: Chef file resource creating systemd unit files followed by daemon-reload; Ansible provides ansible.builtin.systemd module with daemon_reload parameter and template module integration

- **Redis configuration post-processing**: Ruby block manipulating config file to remove deprecated directives; evaluate whether redisio-generated config issues persist with Ansible redis roles, or pre-template correct configuration

- **Package installation across OS families**: Cookbooks support both Ubuntu/Debian and CentOS/RHEL; use ansible.builtin.package with OS-specific variable files (vars/Debian.yml, vars/RedHat.yml) for package name differences (e.g., www-data vs nginx user)

### Migration Order

1. **nginx-multisite** (Priority 1: Foundation service, ~1 week)
   - Low-to-moderate complexity; well-documented patterns
   - Core infrastructure component required by other services
   - Template migration straightforward; security hardening well-understood
   - Recommended approach: Start with basic nginx installation and site configuration, then layer security features (SSL, fail2ban, UFW, sysctl) incrementally
   - Testing: Verify each site accessible via HTTPS, security headers present, firewall rules active

2. **cache** (Priority 2: Support service, ~3-4 days)
   - Low complexity with single external dependency consideration
   - Memcached is straightforward package installation
   - Redis requires attention to authentication and config post-processing hack
   - Evaluate whether Ansible Redis roles avoid the deprecated directive issue
   - Testing: Verify redis-cli authentication, memcached telnet connectivity

3. **fastapi-tutorial** (Priority 3: Application service, ~3-4 days)
   - Moderate complexity due to multi-step deployment (git, venv, pip, PostgreSQL, systemd)
   - Dependencies on PostgreSQL cookbook patterns (user/database creation)
   - Consider using geerlingguy.postgresql role for database management
   - Python virtual environment management well-supported in Ansible
   - Testing: Verify application starts via systemd, database connectivity, HTTP responses on port 8000

### Assumptions

1. **No external Puppet/Salt/PowerShell integration**: Repository appears to be pure Chef; no mixed technology patterns detected

2. **Development/testing environment only**: Self-signed certificates, generic passwords, and Vagrant configuration suggest this is not production-ready; production deployment will require proper secrets management and CA-signed certificates

3. **Ubuntu/Debian is primary target**: Package names (www-data user, apt-get in provision script) and service names suggest Debian-family Linux; CentOS support declared but not tested in current Vagrantfile

4. **Single-server deployment model**: No evidence of multi-node orchestration, load balancing, or clustering; all services deployed to single host

5. **No existing Ansible infrastructure**: Assumes greenfield Ansible migration; no existing roles, playbooks, or inventory to integrate with

6. **Chef Server not in use**: Repository uses chef-solo with local cookbook paths; no Chef Server, Policyfiles, or cookbook version pinning beyond Berkshelf

7. **No Windows targets**: All cookbooks are Linux-specific; no PowerShell DSC or Windows-specific resources

8. **Static site content**: HTML files in cookbooks/nginx-multisite/files/default/ are static; no dynamic content generation or CMS integration

9. **No monitoring/logging integration**: No evidence of Nagios, Prometheus, ELK, or similar monitoring; only local nginx access/error logs

10. **No backup/disaster recovery**: No backup scripts, database dumps, or DR procedures in repository

11. **Git repository is publicly accessible**: FastAPI tutorial cloned from public GitHub repo (https://github.com/dibanez/fastapi_tutorial.git); may need authentication for private repos

12. **Python requirements.txt exists**: FastAPI recipe assumes requirements.txt in repository root; may need verification

13. **PostgreSQL version compatibility**: No specific PostgreSQL version pinned; default system package version assumed compatible with FastAPI application

14. **Redis deprecated directives issue**: Cache cookbook includes Ruby block hack to remove replica-* directives; unclear if this is Redis version-specific or redisio cookbook bug; investigate if Ansible Redis roles have same issue

15. **No SELinux considerations**: No SELinux booleans or contexts configured; may need attention if deploying to RHEL/CentOS with SELinux enforcing

16. **No external load balancer or proxy**: Nginx acts as direct-facing web server; no upstream proxy, CDN, or load balancer integration

17. **Development ports and IPs hardcoded**: Vagrant uses 192.168.121.10 and forwarded ports 8080/8443; production will need parameterized networking

18. **No CI/CD pipeline**: No evidence of Jenkins, GitLab CI, GitHub Actions, or automated testing; migration testing will be manual or require new CI pipeline

19. **No configuration drift detection**: No Chef InSpec, ServerSpec, or compliance scanning; Ansible-based testing (Molecule, Testinfra) not yet implemented

20. **Fedora 42 in Vagrantfile is a typo or future version**: As of this writing, Fedora 42 does not exist; likely should be Fedora 38-40 or ubuntu/jammy64 based on cookbook metadata support declarations
