# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 5 custom site modules implementing a multi-tier application infrastructure. The migration involves converting Puppet profiles and roles to Ansible roles, with moderate complexity due to Hiera data hierarchies, PuppetDB queries, and custom functions. Estimated timeline: 6-8 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and system utilities with MOTD management and package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions, Bolt tasks, MOTD template management, cross-platform OS support

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL database, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment, database URL generation via custom functions, strict dependency chains, environment file templating, log rotation

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend discovery via PuppetDB queries, SSL/TLS configuration, custom error pages, stats authentication, firewall rules

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, package version control, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: Dynamic cluster member discovery, memory policy configuration, password authentication

**role**:
- Description: Role composition layer combining base profiles with service-specific profiles
- Path: site-modules/role
- Technology: Puppet
- Key Features: Profile orchestration, dependency ordering, Linux-specific path configuration

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for development/testing

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level data hierarchy (node → OS family → environment → common) requiring Ansible equivalent
- `data/`: Hierarchical configuration data with environment-specific overrides and OS-specific parameters
- `manifests/site.pp`: Node classification entry point requiring conversion to Ansible inventory
- `Vagrantfile`: Development environment configuration for testing
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on metadata.json specifications
- **Virtual Machine Technology**: Not specified in configurations
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general modules for common functions
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble for file concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw for firewall management
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git for repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd for service management
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt for package management

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in common.yaml including HAProxy stats password, database password, Redis password, and application secret key - migrate to Ansible Vault
- **SSL/TLS Configuration**: HAProxy SSL certificate and key paths require secure file distribution via Ansible Vault or external certificate management
- **SSH Hardening**: SSH configuration parameters in Hiera data need migration to Ansible SSH hardening roles
- **Database Authentication**: PostgreSQL user credentials stored in Hiera require Ansible Vault encryption
- **Service Authentication**: Redis cluster authentication and HAProxy stats authentication need secure credential management
- **Application Secrets**: Application secret keys and environment variables require Ansible Vault protection

### Technical Challenges

- **PuppetDB Query Migration**: profile_haproxy and profile_redis_cluster use PuppetDB queries for dynamic node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 filters or custom modules
- **Hiera Data Hierarchy**: 4-level hierarchy (node/OS/environment/common) requires Ansible group_vars and host_vars structure redesign
- **Dependency Ordering**: Strict class containment and dependency chains need conversion to Ansible task dependencies and handlers
- **Template Complexity**: ERB and EPP templates require conversion to Jinja2 with variable mapping
- **Cross-Platform Support**: OS-specific data files need migration to Ansible when/vars conditional logic

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions establish baseline patterns
2. **profile_postgresql** (moderate complexity) - Database layer with repository management but minimal dependencies
3. **profile_redis_cluster** (moderate complexity) - Cache layer with PuppetDB dependency requiring inventory redesign
4. **profile_app_stack** (high complexity) - Application layer with custom functions and strict dependency chains
5. **profile_haproxy** (highest complexity) - Load balancer with dynamic discovery, SSL, and firewall integration
6. **role** (final integration) - Role composition layer requiring all profiles to be completed

### Assumptions

- PuppetDB functionality will be replaced with Ansible inventory management and group-based node discovery
- Current Hiera data structure can be flattened into Ansible group_vars/host_vars without breaking environment isolation
- Custom Puppet functions can be replaced with equivalent Jinja2 filters or Ansible modules
- SSL certificate management is handled externally and certificates are available for Ansible file distribution
- Testing infrastructure (Vagrant, containers) will be adapted to support Ansible playbook testing
- Node classification currently handled by site.pp will migrate to Ansible inventory with appropriate group assignments
- Development team has access to current Puppet environments for validation and testing during migration
- External dependencies (package repositories, network connectivity) remain consistent between Puppet and Ansible deployments