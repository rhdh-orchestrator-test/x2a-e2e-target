# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with a role-profile-component pattern implementing a full application stack. The migration involves 6 custom modules, 7 external Forge dependencies, and a complex Hiera hierarchy with environment-specific configurations. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for planning, 4-6 weeks for core migration, and 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and Bolt tasks with MOTD management and utility package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types (config_entry, create_dir), Puppet functions (ensure_value, normalize_port), Facter facts, Bolt plans and tasks, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator with Python app deployment, PostgreSQL integration, and systemd service management using strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, systemd service templates, environment file generation, log rotation, health check scripts, monitoring integration

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and dynamic service discovery via PuppetDB queries
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, backend configuration templates, firewall rule management, SSL certificate handling, custom error pages, stats authentication

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with repository management and service control
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: Version-specific package installation, repository configuration, service management, OS-specific package names

**profile_redis_cluster**:
- Description: Redis cluster configuration with dynamic node discovery using PuppetDB queries and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB integration for cluster member discovery, memory policy configuration, password authentication, custom Facter facts for role detection

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing compatibility layer for PuppetDB queries in test environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Custom Puppet function implementation, PuppetDB query abstraction

**profile** (namespace module):
- Description: Profile namespace module containing component profiles for base, app, cache, and loadbalancer configurations
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Namespace organization for profile classes

**role**:
- Description: Role definitions implementing the role-profile-component pattern with app_server, app_stack, haproxy, and redis_cluster roles
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role composition, dependency ordering, OS-specific path configuration

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `hiera.yaml`: 4-level hierarchy (node → OS family → environment → common) requiring Ansible variable precedence mapping
- `environment.conf`: Module path configuration defining site-modules and modules directories
- `manifests/site.pp`: Node classification and test repository setup requiring conversion to Ansible inventory and playbooks
- `data/`: Hiera data files with environment-specific configurations requiring migration to Ansible group_vars and host_vars
- `Vagrantfile`: Development environment configuration for testing
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-OS support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant configuration suggesting VirtualBox/VMware compatibility)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template and assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded passwords**: Multiple plaintext passwords found in Hiera data (haproxy stats, database, Redis, application secret key) requiring migration to Ansible Vault
- **SSL certificate management**: HAProxy SSL configuration with certificate and key paths requiring secure certificate deployment strategy
- **Database credentials**: PostgreSQL connection strings with embedded passwords requiring vault encryption
- **SSH hardening**: SSH configuration parameters in Hiera requiring migration to ansible.posix.sshd_config
- **Service authentication**: Stats interfaces and monitoring endpoints with authentication credentials requiring vault management
- **Git repository access**: Application deployment from Git repositories requiring SSH key or token management

### Technical Challenges

- **PuppetDB dependency**: Redis cluster and HAProxy discovery features rely on PuppetDB queries requiring replacement with Ansible dynamic inventory or service discovery
- **Custom Puppet functions**: profile_app_stack::app_db_url and other custom functions requiring conversion to Jinja2 filters or Ansible modules
- **Complex Hiera hierarchy**: 21-level hierarchy in HAProxy module requiring careful variable precedence mapping in Ansible
- **Strict dependency chains**: Application stack orchestration with notify relationships requiring Ansible handlers and task ordering
- **Facter custom facts**: Custom facts for platform info, HAProxy version, and Redis role requiring conversion to Ansible custom facts or setup module extensions
- **Bolt integration**: Plans and tasks in base_utils module requiring conversion to Ansible playbooks or ad-hoc commands
- **Template complexity**: ERB and EPP templates with complex logic requiring Jinja2 conversion and testing

### Migration Order

1. **base_utils** (low risk, foundational): Utility functions, MOTD management, and package installation - provides foundation for other modules
2. **profile_postgresql** (moderate complexity): Database server setup with minimal dependencies - enables application stack testing
3. **profile_app_stack** (high complexity): Core application deployment with database integration - central to the infrastructure
4. **profile_haproxy** (high complexity): Load balancer with service discovery - depends on application stack for backend configuration
5. **profile_redis_cluster** (high complexity): Cluster configuration with PuppetDB dependencies - requires service discovery replacement
6. **role definitions** (low risk): Role composition and node classification - final integration layer

### Assumptions

- PuppetDB service discovery can be replaced with static configuration or Ansible dynamic inventory during initial migration
- Custom Puppet functions can be adequately replaced with Jinja2 templates and Ansible filters
- The 21-level Hiera hierarchy complexity is necessary and will be preserved in Ansible variable structure
- Current hardcoded passwords in Hiera are acceptable for development/testing and will be properly vaulted in production
- Bolt plans and tasks are actively used and require Ansible playbook equivalents rather than removal
- The role-profile-component pattern should be preserved in Ansible role structure
- Multi-OS support (RHEL, Debian, Ubuntu) is required and will be maintained through Ansible conditionals
- Container-based testing infrastructure will be migrated to Ansible testing frameworks
- Git repository deployment pattern with specific revisions will be maintained in Ansible
- Systemd service management approach is preferred over other init systems
- Current firewall management approach should be preserved (iptables/firewalld based on OS)
- SSL certificate management will use file-based certificates rather than automated certificate authorities
- Application monitoring integration points are required and should be preserved in Ansible implementation