# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with 6 custom modules implementing a multi-tier application stack. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types (config_entry, create_dir), Puppet functions (ensure_value, normalize_port), Bolt tasks and plans, MOTD template management, Facter facts

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Gunicorn WSGI server configuration, PostgreSQL database integration, systemd service hardening, custom Puppet function for database URL generation, log rotation, health monitoring

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, stats interface, and PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: SSL/TLS configuration, backend health checks, stats dashboard, firewall integration, custom error pages, 21-level Hiera hierarchy support

**profile_postgresql**:
- Description: PostgreSQL installation and configuration with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository setup, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration for cluster member discovery, memory policy configuration, custom Facter facts for Redis role detection

**role**:
- Description: Role definitions orchestrating multiple profiles for complete server configurations (app_server, app_stack, haproxy, redis_cluster)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Profile composition, dependency ordering, OS-specific path management

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) requiring Ansible variable precedence mapping
- `environment.conf`: Module path configuration for Puppet environments
- `data/common.yaml`: Global configuration data with hardcoded passwords and application settings
- `data/environment/`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Main site manifest (not present in tree, likely minimal)
- `vagrant-provision.sh`: Development environment provisioning script
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (multi-platform support required)
- **Virtual Machine Technology**: Not specified (supports containerized testing via Containerfile)
- **Cloud Platform**: Not specified (infrastructure-agnostic design)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template assembly or lineinfile modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and apt modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in Hiera data:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password" 
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
  - Migration approach: Implement Ansible Vault for all credential storage
- **SSL/TLS Configuration**: HAProxy module supports SSL termination with certificate management requiring secure certificate deployment patterns
- **Systemd Security Hardening**: Application service template includes NoNewPrivileges, ProtectSystem, ProtectHome, PrivateTmp - preserve these security controls in Ansible systemd units
- **PuppetDB Queries**: Redis cluster uses PuppetDB for node discovery - replace with Ansible inventory groups or dynamic inventory scripts

### Technical Challenges

- **Complex Hiera Hierarchy**: 21-level hierarchy in HAProxy module requires careful Ansible variable precedence mapping across group_vars, host_vars, and role defaults
- **Custom Puppet Functions**: profile_app_stack::app_db_url() function needs conversion to Ansible Jinja2 filter or lookup plugin
- **PuppetDB Integration**: Redis cluster discovery via PuppetDB queries requires replacement with Ansible inventory-based service discovery
- **Strict Dependency Chains**: Application stack uses Puppet's contain/require syntax for ordering - implement with Ansible handlers and task dependencies
- **Cross-Platform Support**: Modules support RHEL, Ubuntu, and Debian - ensure Ansible roles handle package manager differences and OS-specific paths
- **Template Complexity**: HAProxy configuration uses both ERB (.erb) and EPP (.epp) templates with complex parameter passing

### Migration Order

1. **base_utils** (low risk, foundational): Utility functions and common configurations used by other modules
2. **profile_postgresql** (moderate complexity): Database foundation required by application stack
3. **profile_app_stack** (high complexity): Core application with multiple dependencies and custom functions
4. **profile_haproxy** (high complexity): Load balancer with SSL and service discovery
5. **profile_redis_cluster** (highest complexity): Requires PuppetDB replacement and cluster coordination
6. **role** (integration phase): Final orchestration layer combining all profiles

### Assumptions

- Test credentials in Hiera data are placeholders and production systems use proper secret management
- PuppetDB service discovery can be replaced with static inventory groups or dynamic inventory plugins
- Current Puppet environments (production, staging) map directly to Ansible inventory groups
- Systemd service hardening requirements remain consistent across migration
- SSL certificate management processes exist outside of Puppet and can be integrated with Ansible
- Application deployment repository structure (referenced in profile_app_stack) remains unchanged
- HAProxy backend discovery patterns can be adapted to Ansible inventory-based approaches
- Container testing infrastructure can be adapted to use Ansible instead of Puppet provisioning
- Multi-platform support requirements (RHEL/Ubuntu/Debian) remain consistent post-migration