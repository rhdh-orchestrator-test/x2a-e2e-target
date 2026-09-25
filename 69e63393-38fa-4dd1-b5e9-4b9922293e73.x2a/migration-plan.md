# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 5 custom modules implementing a multi-tier application infrastructure. The migration involves converting role-based profiles for application stacks, load balancing, database services, and caching layers. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB dependencies and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions, Bolt tasks, platform-specific package management, MOTD templating

**profile_app_stack**:
- Description: Full application stack orchestrator with Python application deployment, PostgreSQL database integration, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, strict dependency chain, environment file templating, logrotate configuration

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, firewall integration, and optional PuppetDB service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL/TLS support, custom error pages, stats authentication, firewall rule management

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery, memory management, and authentication
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration, cluster node discovery, memory policy configuration, password authentication

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy/Collections
- `environment.conf`: Module path configuration - translate to ansible.cfg and collection requirements
- `hiera.yaml`: 4-level data hierarchy (node → OS → environment → common) - migrate to Ansible group_vars/host_vars structure
- `data/common.yaml`: Global configuration defaults including credentials - requires Ansible Vault conversion
- `data/environment/*.yaml`: Environment-specific overrides - convert to group_vars structure
- `manifests/site.pp`: Node classification logic - migrate to Ansible inventory and playbooks
- `Vagrantfile`: Development environment setup - update for Ansible provisioning

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on metadata.json operatingsystem_support
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general modules
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository

### Security Considerations

- **Hiera Data Encryption**: Current setup uses plain YAML files with embedded credentials - migrate to Ansible Vault for sensitive data
- **Database Credentials**: PostgreSQL and Redis passwords stored in Hiera common.yaml - encrypt with ansible-vault
- **Application Secrets**: Secret keys and API tokens in configuration files - implement proper secret management
- **SSL/TLS Certificates**: HAProxy SSL configuration references certificate paths - ensure secure certificate deployment
- **SSH Hardening**: SSH configuration in Hiera data - translate to ansible.posix.sshd_config module
- **Firewall Rules**: HAProxy firewall integration - migrate to appropriate Ansible firewall modules
- **Service Authentication**: HAProxy stats password and Redis authentication - secure with Vault encryption

### Technical Challenges

- **PuppetDB Integration**: profile_redis_cluster uses PuppetDB queries for node discovery - replace with Ansible inventory-based discovery or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function builds database URLs - convert to Jinja2 templates or custom Ansible filters
- **Hiera Hierarchy**: 4-level data hierarchy with automatic parameter lookup - redesign using Ansible's group_vars/host_vars precedence
- **Dependency Ordering**: Strict class containment and dependency chains - translate to Ansible task dependencies and handlers
- **Cross-Platform Support**: OS-specific data files and package management - implement using Ansible's when conditionals and vars files
- **Template Engines**: Mix of ERB and EPP templates - convert all to Jinja2 format
- **Bolt Tasks**: Custom shell scripts and JSON task definitions - migrate to Ansible ad-hoc commands or modules

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions needed by other modules
2. **profile_postgresql** (moderate complexity) - Database layer with minimal external dependencies
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB replacement strategy before migration
4. **profile_app_stack** (high complexity) - Complex orchestration with multiple dependencies
5. **profile_haproxy** (moderate complexity) - Load balancer with firewall integration

### Assumptions

- **PuppetDB Replacement**: Assumes Ansible inventory or dynamic inventory will replace PuppetDB node discovery functionality
- **Hiera Data Migration**: Assumes all Hiera YAML files will be converted to appropriate Ansible variable structures
- **Service Discovery**: Assumes static inventory or external service discovery will replace PuppetDB queries
- **Certificate Management**: Assumes existing SSL certificate deployment processes will be maintained
- **Monitoring Integration**: Assumes existing monitoring systems (referenced in profile_app_stack::monitoring) will be compatible with Ansible-managed services
- **Git Repository Access**: Assumes application repositories referenced in profile_app_stack remain accessible with same authentication
- **Python Environment**: Assumes Python application deployment patterns will translate directly to Ansible pip and virtualenv modules
- **Database Initialization**: Assumes PostgreSQL database and user creation processes are handled outside these profiles
- **Network Configuration**: Assumes firewall and network policies will be managed consistently across Puppet and Ansible phases
- **Backup Procedures**: Assumes existing backup scripts (backup.sh in profile_app_stack) will be integrated into Ansible workflows