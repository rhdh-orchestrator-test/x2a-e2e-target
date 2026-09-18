# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier application stack architecture. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, custom functions, and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with custom Puppet functions and Bolt tasks
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package arrays, custom functions (ensure_value, normalize_port), Bolt health check tasks, platform-specific Hiera data

**profile_app_stack**:
- Description: Full application stack orchestrator with Python application deployment, PostgreSQL database integration, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, strict dependency chains, environment file templating, logrotate configuration

**profile_haproxy**:
- Description: HAProxy load balancer with multi-backend support, SSL termination, stats interface, and optional PuppetDB-based backend discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL certificate management, firewall integration, custom error pages, backend health checks

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, package version control, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster node discovery, memory policy configuration, password authentication

**profile**:
- Description: Thin wrapper profiles that delegate to main profile modules and provide role composition
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS profile with NTP/syslog management, application stack wrapper, HAProxy wrapper

**role**:
- Description: Role classes that compose profiles for specific node types (app servers, load balancers)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Linux-specific exec path defaults, profile composition with dependency ordering

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for development/testing

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules, modules, and base module paths
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) with YAML data backend
- `data/common.yaml`: Environment-wide configuration including NTP servers, SSH hardening, application parameters, and database credentials
- `data/environment/*.yaml`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Main site manifest (not examined but likely contains node classification)
- `Vagrantfile`: Local development environment configuration
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Based on metadata.json files, targets Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, and Debian 11/12. Default to Red Hat Enterprise Linux 9 for primary migration target.
- **Virtual Machine Technology**: Vagrant configuration present suggests VirtualBox/VMware for development. Production VM platform not specified in examined files.
- **Cloud Platform**: No cloud-specific configurations detected in the examined files. Likely on-premises or cloud-agnostic deployment.

## Migration Approach

### Key Dependencies to Address
- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template module and file assembly techniques
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt modules
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module

### Security Considerations
- **Hardcoded passwords**: Multiple plaintext passwords found in common.yaml (haproxy stats, database, Redis, application secret key) - migrate to Ansible Vault
- **SSL certificate management**: HAProxy SSL configuration references certificate paths - implement proper certificate deployment with Ansible Vault
- **SSH hardening**: SSH configuration parameters in Hiera data need migration to Ansible ssh role
- **Database credentials**: PostgreSQL connection strings with embedded passwords need Ansible Vault encryption
- **Application secrets**: Secret keys and API tokens in configuration templates require secure variable management
- **Service account passwords**: Application user credentials and service authentication need vault protection

### Technical Challenges
- **PuppetDB queries**: profile_redis_cluster uses PuppetDB for node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet functions**: profile_app_stack::app_db_url function needs conversion to Jinja2 template or Ansible filter plugin
- **21-level Hiera hierarchy**: Complex data lookup system needs restructuring into Ansible group_vars and host_vars with proper precedence
- **Strict dependency chains**: Puppet's contain/require relationships need conversion to Ansible handler notifications and task dependencies
- **ERB/EPP templates**: Template syntax conversion from Ruby ERB to Jinja2, including function calls and variable scoping
- **Bolt tasks and plans**: health_check.pp and rolling_restart.pp plans need conversion to Ansible playbooks with proper error handling
- **Custom types and providers**: Puppet custom types (ensure_value, log_level, port) need conversion to Ansible custom modules or validation

### Migration Order
1. **base_utils** (low risk, foundational) - Common utilities and MOTD management, no external dependencies
2. **profile_postgresql** (moderate complexity) - Database foundation needed by application stack
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB query replacement and cluster logic
4. **profile_haproxy** (moderate complexity) - Load balancer with SSL and firewall integration
5. **profile_app_stack** (highest complexity) - Full application deployment with custom functions and strict dependencies
6. **profile and role wrappers** (low complexity) - Simple delegation classes, migrate after core profiles

### Assumptions
- **Node classification**: Assuming site.pp contains node classification that will need conversion to Ansible inventory groups
- **External systems**: PuppetDB availability during migration for testing node discovery replacement strategies
- **Certificate management**: SSL certificates are managed externally or through a separate process not visible in this repository
- **Database initialization**: PostgreSQL database and user creation processes may exist outside this codebase
- **Monitoring integration**: profile_app_stack references monitoring class but implementation not visible in examined files
- **Network configuration**: Firewall rules and network policies may have dependencies not captured in the examined modules
- **Backup procedures**: backup.sh script in profile_app_stack suggests external backup processes that need coordination
- **Service discovery**: HAProxy backend discovery mechanism needs clarification for Ansible equivalent implementation
- **Development workflow**: Vagrant-based development environment will need Ansible equivalent for testing
- **Deployment pipeline**: Current Puppet deployment and testing processes need documentation for Ansible migration planning