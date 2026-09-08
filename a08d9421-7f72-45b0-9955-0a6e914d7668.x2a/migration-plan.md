# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a mature Puppet control repository with a role-profile pattern implementing a multi-tier web application stack. The migration involves 6 custom modules, 7 external Puppet Forge dependencies, and a sophisticated Hiera hierarchy with environment-specific configurations. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with moderate complexity due to the structured architecture and comprehensive configuration management.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and Bolt tasks with MOTD management and utility package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Facter facts, Bolt plans and tasks, ERB templates for MOTD, cross-platform OS support

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL database, systemd service management, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Strict dependency chain orchestration, custom Puppet function for database URL generation, Git repository deployment via vcsrepo, systemd service templates, log rotation configuration

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, service discovery, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration via EPP templates, SSL/TLS configuration with cipher management, stats interface with authentication, PuppetDB-based service discovery, firewall rule management

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with version-specific package management and repository setup
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: Version-specific PostgreSQL installation, repository management for different OS families, service lifecycle management

**profile_redis_cluster**:
- Description: Redis cluster configuration with memory management, authentication, and PuppetDB-based node discovery for cluster formation
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query for cluster node discovery, memory policy configuration, password authentication, cluster-aware configuration templates

**role**:
- Description: Role definitions implementing the role-profile pattern for application servers and load balancers with OS-specific path management
- Path: site-modules/role
- Technology: Puppet
- Key Features: Composition layer for profiles, OS-specific exec path configuration, dependency ordering between base and application profiles

### Infrastructure Files

- `Puppetfile`: Puppet Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt, and inifile modules
- `environment.conf`: Module path configuration defining site-modules, modules, and base module paths
- `hiera.yaml`: 4-level hierarchy configuration (node-specific, OS family, environment, common) with YAML data backend
- `data/common.yaml`: Environment-level defaults including NTP, SSH hardening, logging, and application configuration with embedded credentials
- `data/environment/*.yaml`: Environment-specific overrides for production and staging environments
- `manifests/site.pp`: Main site manifest for node classification and global configuration
- `Vagrantfile`: Local development environment configuration for testing Puppet manifests
- `vagrant-provision.sh`: Vagrant provisioning script for development setup

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-platform support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template assembly or blockinfile modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hiera Data Encryption**: Current setup uses plain-text YAML files with embedded credentials (database passwords, Redis passwords, HAProxy stats passwords, application secret keys) - migrate to Ansible Vault for sensitive data encryption
- **SSL/TLS Configuration**: HAProxy module includes SSL cipher management and certificate handling - ensure proper certificate deployment and cipher suite configuration in Ansible
- **SSH Hardening**: Current SSH configuration includes security settings (permit_root_login: false, client_alive_interval) - maintain these security postures in Ansible
- **Firewall Management**: Profile_haproxy includes firewall integration - ensure firewall rules are properly migrated and tested
- **Service Account Management**: Application stack uses dedicated service accounts (appuser) - ensure proper user/group creation and permissions in Ansible

### Technical Challenges

- **PuppetDB Query Migration**: profile_redis_cluster uses PuppetDB queries for dynamic node discovery - replace with Ansible inventory-based service discovery or dynamic inventory scripts
- **Custom Puppet Functions**: base_utils and profile_app_stack include custom Puppet functions (ensure_value, normalize_port, app_db_url) - reimplement as Ansible custom filters or lookup plugins
- **Hiera Hierarchy Complexity**: 4-level hierarchy with node-specific, OS family, environment, and common data - migrate to Ansible group_vars and host_vars structure with proper precedence
- **Strict Dependency Ordering**: profile_app_stack enforces strict dependency chains with notify relationships - implement using Ansible handlers and task dependencies
- **Template Complexity**: HAProxy configuration uses complex ERB templates with conditional SSL configuration - migrate to Jinja2 templates with equivalent logic
- **Facter Custom Facts**: base_utils includes custom Facter facts (platform_info, haproxy_version) - replace with Ansible custom facts or setup module extensions

### Migration Order

1. **base_utils** (low risk, foundational) - Migrate utility functions and basic system configuration first as other modules depend on these utilities
2. **profile_postgresql** (moderate complexity) - Database layer migration with version-specific package management and repository configuration
3. **profile_redis_cluster** (moderate complexity) - Cache layer with cluster discovery challenges requiring inventory-based solutions
4. **profile_app_stack** (high complexity) - Application orchestration with strict dependencies, custom functions, and service management
5. **profile_haproxy** (high complexity) - Load balancer with SSL configuration, dynamic backends, and firewall integration
6. **role** (low complexity) - Final composition layer after all profiles are migrated and tested

### Assumptions

- The target Ansible environment will use similar OS distributions (RHEL 8/9, Debian 11/12, Ubuntu 22.04/24.04) as specified in Puppet metadata
- Ansible Vault will be used to replace plain-text credential storage currently in Hiera YAML files
- The existing 4-level Hiera hierarchy can be effectively mapped to Ansible's group_vars/host_vars structure
- PuppetDB-based service discovery can be replaced with Ansible inventory-based approaches or dynamic inventory scripts
- The role-profile pattern will be maintained in Ansible using role composition and variable precedence
- Custom Puppet functions can be successfully reimplemented as Ansible filters or lookup plugins without functionality loss
- The existing SSL/TLS and firewall configurations are compatible with target Ansible modules
- Development and testing environments (Vagrant-based) will be migrated to support Ansible playbook testing
- The strict dependency ordering and notification patterns can be replicated using Ansible handlers and task dependencies