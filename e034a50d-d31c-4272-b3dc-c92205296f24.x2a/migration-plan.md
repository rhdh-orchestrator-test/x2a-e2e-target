# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 8 custom modules implementing a multi-tier application stack. The migration involves converting profile-based architecture, Hiera data hierarchies, and PuppetDB queries to Ansible equivalents. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with moderate complexity due to the structured profile/role pattern and cross-module dependencies.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with Bolt task support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package arrays, custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks and rolling restarts

**profile_app_stack**:
- Description: Full application stack orchestrator with strict dependency chain for Python applications, PostgreSQL database integration, and systemd service management
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, database URL generation via custom functions, Gunicorn worker configuration, systemd service templates, log rotation, environment file management

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL/TLS configuration, stats authentication, firewall integration, custom error pages, backend discovery via PuppetDB queries

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG APT repository configuration, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster profile using puppet-redis module with PuppetDB node discovery for cluster member identification
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster topology, memory policy configuration, password authentication, cluster node discovery

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing compatibility layer for PuppetDB queries in test environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query function for testing and development environments

**profile (namespace module)**:
- Description: Profile namespace module containing base OS configuration, application stack wrappers, cache management, and load balancer profiles
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS hardening (chrony NTP, rsyslog), application stack delegation, modular profile organization

**role (namespace module)**:
- Description: Role definitions implementing the roles-and-profiles pattern for application servers, HAProxy nodes, and Redis clusters
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, profile composition, dependency ordering between base and application profiles

### Infrastructure Files

- `Puppetfile`: External module dependencies including puppetlabs-stdlib, puppetlabs-concat, puppetlabs-firewall, puppetlabs-vcsrepo, puppet-redis, and puppetlabs-apt
- `environment.conf`: Module path configuration defining site-modules as primary module source
- `hiera.yaml`: 4-level Hiera hierarchy (per-node, per-OS, per-environment, common) requiring conversion to Ansible variable precedence
- `manifests/site.pp`: Main site manifest for node classification (not examined but likely contains role assignments)
- `data/`: Hiera data directory with environment-specific and common configuration data
- `Vagrantfile`: Development environment configuration for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (based on metadata.json operatingsystem_support declarations)
- **Virtual Machine Technology**: Not specified in configurations
- **Cloud Platform**: Not specified in configurations

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general modules for common functions
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module for repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration tasks
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded passwords in Hiera data**: Database passwords, HAProxy stats passwords, Redis authentication, and application secret keys are stored in plain text in common.yaml and require migration to Ansible Vault
- **SSL/TLS certificate management**: HAProxy SSL configuration references certificate paths that need secure deployment via Ansible Vault or external certificate management
- **SSH hardening configurations**: SSH client alive intervals and root login restrictions configured via Hiera need conversion to ansible.posix.sshd_config
- **Service authentication**: Application database credentials and Redis passwords require vault encryption
- **Credential types identified per module**:
  - profile_app_stack: Database passwords, application secret keys (2 credential types)
  - profile_haproxy: Stats interface passwords, SSL certificate references (2 credential types)
  - profile_redis_cluster: Redis authentication passwords (1 credential type)

### Technical Challenges

- **PuppetDB query conversion**: profile_redis_cluster and profile_haproxy use PuppetDB queries for service discovery - requires replacement with Ansible inventory plugins or dynamic inventory scripts
- **Custom Puppet functions**: base_utils contains custom functions (ensure_value, normalize_port) and profile_app_stack uses app_db_url function - need conversion to Ansible filters or custom modules
- **Hiera hierarchy complexity**: 4-level hierarchy with per-node, per-OS, per-environment precedence requires careful mapping to Ansible variable precedence and group_vars structure
- **Strict dependency ordering**: profile_app_stack implements strict dependency chains using Puppet's contain and chaining operators - requires conversion to Ansible handlers and task dependencies
- **Template complexity**: HAProxy configuration template uses complex ERB logic for SSL and backend configuration - needs conversion to Jinja2 with equivalent conditional logic
- **Bolt task integration**: base_utils includes Bolt tasks for health checks and rolling restarts - requires conversion to Ansible playbooks or custom modules

### Migration Order

1. **base_utils** (low risk, foundational): Core utility functions and MOTD management with minimal dependencies
2. **profile_postgresql** (moderate complexity): Database installation with repository management, required by app stack
3. **profile_redis_cluster** (moderate complexity): Cache layer with PuppetDB dependency requiring inventory solution
4. **profile_app_stack** (high complexity): Application deployment with multiple dependencies and custom functions
5. **profile_haproxy** (high complexity): Load balancer with complex templating and service discovery
6. **profile and role modules** (integration phase): Namespace modules and role definitions after all profiles are migrated

### Assumptions

- The repository uses Puppet 7.x based on metadata.json requirements, indicating modern Puppet features that may not have direct Ansible equivalents
- PuppetDB is available in the current environment for service discovery queries, requiring alternative discovery mechanisms in Ansible
- The roles-and-profiles pattern suggests a mature Puppet implementation with clear separation of concerns that should map well to Ansible role structure
- SSL certificates referenced in HAProxy configuration are managed externally and will need integration with Ansible certificate management workflows
- The 21-level Hiera hierarchy mentioned in profile_haproxy comments suggests complex data organization that may require significant restructuring in Ansible
- Bolt tasks are actively used for operational procedures and will need equivalent Ansible playbook implementations
- The application stack assumes systemd-based service management on target systems
- Git repositories referenced in profile_app_stack are accessible from Ansible control nodes with appropriate authentication
- Custom Puppet functions perform business logic that must be preserved during migration to Ansible filters or modules