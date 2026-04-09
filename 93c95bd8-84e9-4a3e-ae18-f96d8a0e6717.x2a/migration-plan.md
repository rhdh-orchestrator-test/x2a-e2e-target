# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security hardening requirements
- SSL certificate management
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Defines the run list and cookbook versions - will be replaced by Ansible playbook structure
- `solo.json`: Contains node configuration data - will be converted to Ansible variables
- `Vagrantfile`: Defines the development VM - will need updates to use Ansible provisioner instead of Chef
- `vagrant-provision.sh`: Shell script for Chef provisioning - will be replaced with Ansible provisioning
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **ssl_certificate (~> 2.1)**: Replace with Ansible crypto modules (community.crypto.openssl_*)
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct configuration tasks

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper certificate generation and permissions
  - Use community.crypto.openssl_* modules for certificate generation
  - Ensure proper file permissions for private keys

- **Firewall Configuration (UFW)**: Maintain firewall rules
  - Use community.general.ufw module to configure firewall rules

- **Fail2ban Configuration**: Maintain intrusion prevention
  - Use Ansible to install and configure fail2ban with appropriate jails

- **SSH Hardening**: Maintain SSH security settings
  - Use ansible.posix.sshd_config module to configure SSH daemon

- **Redis Authentication**: Maintain Redis password protection
  - Ensure Redis password is stored securely in Ansible Vault

- **PostgreSQL Security**: Maintain database user security
  - Store database credentials in Ansible Vault
  - Use postgresql_* modules to manage users and permissions

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation dynamically generates site configurations based on node attributes. Ansible templates will need to replicate this dynamic behavior.
  - Solution: Use Ansible template module with loops over site variables

- **SSL Certificate Generation**: Self-signed certificates are currently generated with custom commands. This will need to be replaced with Ansible's crypto modules.
  - Solution: Use community.crypto.openssl_* modules to generate certificates

- **Service Interdependencies**: The FastAPI application depends on PostgreSQL being configured first. Ansible handlers and proper task ordering will be needed.
  - Solution: Use Ansible meta dependencies between roles and proper handler notification

- **Redis Configuration Workarounds**: The current implementation includes a "hack" to fix Redis configuration. This will need a cleaner approach in Ansible.
  - Solution: Create proper Redis configuration templates rather than post-editing the config file

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add virtual host configuration
   - Add security hardening features

2. **cache** (moderate complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on other services)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same network configuration (ports, IP addresses) will be maintained
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
4. The FastAPI application source will continue to be available at the specified Git repository
5. Redis and Memcached configurations don't require significant customization beyond what's currently implemented
6. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
7. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       └── all.yml
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   ├── cache/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi-tutorial/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── requirements.yml
└── Vagrantfile
```

## Next Steps

1. Create a detailed variable mapping from Chef attributes to Ansible variables
2. Set up Ansible Vault for sensitive information (Redis password, PostgreSQL credentials)
3. Develop and test each role individually
4. Create integration tests to verify the complete stack works together
5. Update documentation for the new Ansible-based deployment process