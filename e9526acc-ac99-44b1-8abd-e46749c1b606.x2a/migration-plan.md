# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 5 custom site modules implementing a multi-tier web application stack. The migration involves converting role-based profiles for application servers, load balancers, databases, and caching layers. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, multi-level Hiera hierarchy, and SSL/TLS configurations.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions, Facter facts, Bolt tasks, ERB templates for MOTD, OS-specific package lists

**profile_app_stack**:
- Description: Full application stack orchestrator with Python application deployment, PostgreSQL database integration, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, strict dependency chains, EPP/ERB templates, logrotate configuration

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, firewall integration, and PuppetDB service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL/TLS configuration, custom error pages, backend discovery, firewall rules, stats authentication

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository management, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery, memory management, and cluster coordination
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for node discovery, Redis configuration templates, cluster role detection via custom facts

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires Ansible Galaxy/Collections mapping
- `environment.conf`: Module path configuration - translate to ansible.cfg
- `hiera.yaml`: 4-level data hierarchy (nodes → OS → environment → common) - migrate to Ansible group_vars/host_vars structure
- `data/common.yaml`: Global configuration with hardcoded passwords - requires Ansible Vault migration
- `data/environment/*.yaml`: Environment-specific overrides - map to Ansible inventory groups
- `manifests/site.pp`: Node classification logic - convert to Ansible inventory and playbooks
- `Vagrantfile`: Development environment - update for Ansible provisioning
- `test/`: Container-based testing - adapt for ansible-test or molecule

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (multi-platform support required)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant development environment)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general modules
- **puppetlabs-concat (9.0.2)**: Use ansible.builtin.assemble or template with loops
- **puppetlabs-firewall (8.1.3)**: Migrate to ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Use community.general.redis modules or custom tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Use ansible.builtin.apt and apt_repository modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in data/common.yaml requiring Ansible Vault migration:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password" 
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
- **SSL/TLS Configuration**: HAProxy SSL termination with certificate path references requiring secure certificate deployment
- **SSH Hardening**: SSH configuration parameters in Hiera data need migration to Ansible SSH role
- **Firewall Rules**: HAProxy firewall integration requires careful port and rule migration
- **Service Authentication**: HAProxy stats interface authentication needs secure credential management

### Technical Challenges

- **PuppetDB Queries**: profile_redis_cluster uses PuppetDB queries for node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Jinja2 template or custom filter
- **21-Level Hiera Hierarchy**: Complex data lookup precedence in profile_haproxy requires careful Ansible variable precedence mapping
- **Strict Dependency Chains**: profile_app_stack enforces strict ordering with notify relationships - implement with Ansible handlers and task dependencies
- **Cross-Platform Support**: Modules support RHEL, Ubuntu, and Debian - ensure Ansible playbooks handle OS-specific variations
- **Template Complexity**: ERB/EPP templates with conditional logic need conversion to Jinja2 with equivalent functionality

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions establish foundation for other modules
2. **profile_postgresql** (moderate complexity) - Database layer with straightforward package/service management
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB query replacement and cluster coordination logic
4. **profile_app_stack** (high complexity) - Complex orchestration with custom functions and strict dependencies
5. **profile_haproxy** (highest complexity) - Most complex with SSL, discovery, firewall integration, and multi-level Hiera

### Assumptions

- Test environment passwords are placeholders and production uses proper secret management
- PuppetDB service discovery can be replaced with static inventory groups or dynamic inventory
- SSL certificates are managed externally and paths can be standardized across environments
- Current Vagrant development workflow can be adapted to support Ansible provisioning
- Firewall provider "none" in test data indicates firewall rules may be disabled in development
- Custom Puppet functions have equivalent Jinja2 filter implementations or can be replaced with templates
- Multi-platform support requirements (RHEL/Ubuntu/Debian) will be maintained in Ansible version
- Container-based testing framework can be adapted for Ansible testing with molecule or similar tools