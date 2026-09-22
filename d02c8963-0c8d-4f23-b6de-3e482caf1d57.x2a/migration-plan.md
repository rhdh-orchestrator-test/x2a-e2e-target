# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier application stack. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, custom functions, and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with Bolt tasks for health checks
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions, Facter facts, MOTD template management, rolling restart plans

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL database, systemd service management, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment, Python environment setup, database URL generation via custom function, systemd service templates, log rotation, strict dependency chain

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and optional PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Multi-level Hiera configuration (21-level hierarchy), SSL/TLS configuration, firewall integration, custom error pages, backend health checks

**profile_postgresql**:
- Description: PostgreSQL installation and configuration with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository management, package version control, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery for automatic cluster member detection
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for node discovery, memory management policies, cluster configuration

**role**:
- Description: Role definitions implementing the roles-and-profiles pattern for application servers and stack nodes
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role composition, profile orchestration, dependency management

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy/Collections
- `environment.conf`: Module path configuration - needs conversion to ansible.cfg
- `hiera.yaml`: 4-level data hierarchy (nodes, OS family, environment, common) - requires Ansible variable precedence design
- `manifests/site.pp`: Node classification and test repository setup - needs conversion to inventory and playbooks
- `data/`: Hiera data files with environment-specific configurations - requires variable file restructuring
- `vagrant-provision.sh`: Development environment setup script - may need updates for Ansible workflow

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in configurations
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository

### Security Considerations

- **Hardcoded credentials in Hiera data**: Database passwords, Redis passwords, HAProxy stats passwords, and application secret keys are stored in plain text in common.yaml
  - profile_app_stack::db_password: "test-db-password"
  - profile_app_stack::secret_key: "test-secret-key"
  - profile_haproxy::stats_password: "test-haproxy-password"
  - profile_redis_cluster::redis_password: "test-redis-password"
- **SSL/TLS certificate management**: HAProxy module references SSL certificate and key paths that need secure handling
- **SSH hardening configurations**: SSH settings in Hiera need migration to Ansible SSH hardening roles
- **Service account management**: Application user/group creation needs secure implementation in Ansible

### Technical Challenges

- **PuppetDB queries**: profile_redis_cluster uses PuppetDB queries for node discovery - requires replacement with Ansible inventory or dynamic inventory scripts
- **Custom Puppet functions**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 filters or custom modules
- **Multi-level Hiera hierarchy**: 21-level hierarchy in profile_haproxy requires careful variable precedence design in Ansible
- **Strict dependency chains**: profile_app_stack enforces strict ordering with contain/require - needs conversion to Ansible handlers and task dependencies
- **Facter custom facts**: base_utils and profile_haproxy include custom Ruby facts that need conversion to Ansible custom facts or setup modules
- **Bolt tasks and plans**: base_utils includes Bolt tasks for health checks and rolling restarts - requires conversion to Ansible playbooks

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions needed by other modules
2. **profile_postgresql** (moderate complexity) - Database layer with minimal dependencies
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB query replacement strategy
4. **profile_app_stack** (high complexity) - Core application with custom functions and strict dependencies
5. **profile_haproxy** (highest complexity) - Load balancer with complex Hiera hierarchy and service discovery
6. **role** (low risk) - Role composition after all profiles are migrated

### Assumptions

- Test environment uses local file:// Git repositories that may need adjustment for Ansible git module
- PuppetDB service discovery can be replaced with static inventory or Ansible dynamic inventory
- Custom Puppet functions can be converted to Jinja2 templates or custom Ansible modules
- Bolt tasks and plans are not critical for initial migration and can be addressed in a later phase
- SSL certificates referenced in HAProxy configuration exist and are accessible to Ansible
- Database and Redis passwords are acceptable as test values and will be replaced with proper secrets management
- The 21-level Hiera hierarchy in profile_haproxy can be simplified in Ansible without losing functionality
- Vagrant development environment will continue to be used with Ansible provisioning
- Operating system support matrix from metadata.json accurately reflects deployment targets