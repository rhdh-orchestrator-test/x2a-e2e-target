# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 5 custom modules implementing a multi-tier application infrastructure. The migration involves converting role-based profiles for application stacks, load balancing, database services, and caching layers. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB dependencies and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, systemd service management, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Strict dependency chain orchestration, custom database URL function, Git repository deployment via vcsrepo, systemd service templates, log rotation configuration

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, stats interface, and optional PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL/TLS configuration, firewall integration, backend health checks, custom error pages, PuppetDB node discovery

**profile_postgresql**:
- Description: PostgreSQL installation and configuration with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository setup, version-specific package installation, service management, cross-platform support (Debian/Ubuntu)

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery, memory management, and clustering support
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration for cluster member discovery, memory policy configuration, custom Facter facts for Redis role detection

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy/Collections
- `environment.conf`: Module path configuration - translate to ansible.cfg and collection requirements
- `hiera.yaml`: 4-level data hierarchy (node → OS → environment → common) - migrate to Ansible group_vars structure
- `data/`: Hierarchical configuration data with environment-specific overrides - convert to group_vars and host_vars
- `manifests/site.pp`: Node classification logic - migrate to Ansible inventory and playbook structure
- `Vagrantfile`: Development environment setup - update for Ansible provisioning
- `test/`: Container-based testing framework - adapt for ansible-test or molecule

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (multi-platform support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin modules and community.general collection
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.service modules
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in Hiera data (haproxy stats, database, Redis, application secret key) - migrate to Ansible Vault
- **SSL/TLS Configuration**: HAProxy SSL certificate and key paths configured via Hiera - implement secure certificate deployment with Ansible Vault
- **SSH Hardening**: SSH configuration parameters in common.yaml - migrate to ansible.posix.sshd_config module
- **Database Credentials**: PostgreSQL user/password combinations in application stack - encrypt with ansible-vault
- **Service Authentication**: Redis password and application secret keys - secure with Ansible Vault encryption
- **Firewall Rules**: HAProxy firewall integration requires careful port management migration

### Technical Challenges

- **PuppetDB Dependencies**: profile_redis_cluster uses PuppetDB queries for cluster member discovery - replace with Ansible inventory-based service discovery or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function builds database URLs - reimplement as Jinja2 template or custom Ansible filter
- **Complex Hiera Hierarchy**: 21-level hierarchy in HAProxy module requires careful group_vars structure design
- **Strict Dependency Chains**: profile_app_stack enforces strict ordering (python → database → app → service → monitoring) - implement with Ansible handlers and task dependencies
- **Cross-Platform Support**: Modules support multiple OS families - design platform-specific variable files and conditional tasks
- **Template Migration**: ERB and EPP templates need conversion to Jinja2 format with different syntax

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions establish baseline
2. **profile_postgresql** (moderate complexity) - Database layer with repository management
3. **profile_app_stack** (high complexity) - Application orchestration with strict dependencies
4. **profile_haproxy** (high complexity) - Load balancer with SSL and discovery features
5. **profile_redis_cluster** (highest complexity) - Clustering with PuppetDB integration requires custom solutions

### Assumptions

- PuppetDB service discovery in Redis cluster can be replaced with Ansible inventory-based approaches or external service discovery tools
- Current Hiera data structure represents production-ready configuration values that should be preserved during migration
- The 4-level Hiera hierarchy (node/OS/environment/common) maps cleanly to Ansible's group_vars precedence system
- Existing SSL certificate management processes can be adapted to Ansible Vault and deployment workflows
- Custom Puppet functions can be reimplemented as Jinja2 filters or lookup plugins without functionality loss
- Multi-platform support requirements (RHEL/Debian/Ubuntu) will be maintained in the Ansible implementation
- Current role-based node classification in site.pp can be migrated to Ansible inventory groups and playbook organization
- Bolt task functionality (health checks, rolling restarts) can be replaced with Ansible ad-hoc commands or playbooks
- Container-based testing framework can be adapted to use Molecule or ansible-test for validation
- External module dependencies from Puppet Forge have equivalent functionality available in Ansible Galaxy collections