# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Defines the Chef policy with run list and cookbook dependencies
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Migration must preserve the self-signed certificate generation for development environments
- **Firewall Configuration (UFW)**: Convert UFW rules to Ansible's `ufw` module
- **fail2ban Configuration**: Migrate fail2ban configuration using Ansible's template module
- **SSH Hardening**: Preserve SSH security settings (root login disabled, password authentication disabled)
- **Redis Authentication**: Ensure Redis password is properly managed in Ansible Vault
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on attributes needs careful translation to Ansible variables and templates
- **SSL Certificate Management**: Ensuring proper permissions and ownership of SSL certificates and keys
- **Service Dependencies**: Maintaining the correct order of service installation and configuration
- **Idempotency**: Ensuring all operations remain idempotent, particularly the database user and database creation tasks

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement site configuration templates
   - Add security hardening (fail2ban, UFW)

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata
2. Self-signed certificates are acceptable for development environments
3. The same security policies (disabled root login, password authentication) will be maintained
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis will continue to require password authentication
6. The Vagrant development environment will be maintained but converted to use Ansible provisioning
7. The directory structure for web content and application files will remain the same

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── tasks/
│   │   ├── templates/
│   │   ├── files/
│   │   └── handlers/
│   ├── cache/
│   │   ├── defaults/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── handlers/
│   └── fastapi-tutorial/
│       ├── defaults/
│       ├── tasks/
│       ├── templates/
│       └── handlers/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── Vagrantfile
└── vagrant-provision.yml
```

## Migration Steps

1. **Setup Ansible Project Structure**
   - Create directory structure as outlined above
   - Set up inventory files for development and production

2. **Create Common Variables**
   - Convert Chef attributes to Ansible variables
   - Set up vault for sensitive information (Redis password, PostgreSQL credentials)

3. **Develop Roles**
   - Create each role with appropriate tasks, templates, and handlers
   - Test each role individually

4. **Create Playbooks**
   - Develop playbooks that combine roles
   - Ensure proper ordering and dependencies

5. **Update Vagrant Configuration**
   - Modify Vagrantfile to use Ansible provisioner
   - Create vagrant-specific inventory and variables

6. **Testing**
   - Test in Vagrant environment
   - Verify all functionality matches original Chef implementation

7. **Documentation**
   - Document each role and its variables
   - Create usage examples and deployment guides