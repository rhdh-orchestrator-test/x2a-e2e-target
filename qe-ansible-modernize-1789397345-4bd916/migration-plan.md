# MIGRATION FROM LEGACY ANSIBLE TO MODERN ANSIBLE

This repository contains a legacy Ansible role that requires modernization to current best practices. The role uses deprecated syntax, insecure patterns, and outdated modules that need to be updated to modern Ansible standards. This is a modernization effort rather than a cross-technology migration.

## Module Migration Plan

This repository contains legacy Ansible code that needs modernization:

### MODULE INVENTORY

**legacy_webserver**:
- Description: Apache HTTP server deployment with SSL support, PHP runtime, optional Docker integration, and Prometheus monitoring capabilities
- Path: roles/legacy_webserver
- Technology: Legacy Ansible (pre-2.9 patterns)
- Key Features: Apache/mod_ssl configuration, firewall management, virtual host setup, conditional Docker installation, node-exporter monitoring

### Infrastructure Files

- `README.md`: Basic project documentation indicating QE testing purpose
- `roles/legacy_webserver/meta/main.yml`: Role metadata with Galaxy info and platform support (EL 7/8)
- `roles/legacy_webserver/defaults/main.yml`: Default variables for vhost configuration, Docker, and monitoring toggles
- `roles/legacy_webserver/tasks/main.yml`: Main task file with deprecated syntax and security issues
- `roles/legacy_webserver/handlers/main.yml`: Service restart handlers using deprecated sudo syntax

### Target Details

- **Operating System**: Red Hat Enterprise Linux 7/8 (as specified in meta/main.yml platforms)
- **Virtual Machine Technology**: Not specified in current configuration
- **Cloud Platform**: Not specified - appears to be generic infrastructure

## Migration Approach

### Key Dependencies to Address
- **httpd**: Continue using system package manager (dnf/yum)
- **mod_ssl**: Continue using system package manager
- **php/php-mysql**: Update to specific PHP version packages for better security
- **firewall-cmd**: Replace shell commands with ansible.posix.firewalld module
- **docker**: Replace deprecated docker_container with community.docker collection

### Security Considerations
- **Deprecated sudo usage**: All tasks use deprecated `sudo: yes` and `sudo_user: root` instead of `become: yes` and `become_user: root`
- **Shell command injection**: Firewall configuration uses shell module with potential command injection risks
- **Missing template files**: Tasks reference missing template files (httpd.conf.j2, vhost.conf.j2) that could cause deployment failures
- **Missing task files**: References non-existent docker_setup.yml include file
- **Hardcoded paths**: Uses hardcoded system paths without variable abstraction
- **No input validation**: Variables lack validation and type checking

### Technical Challenges
- **Missing templates**: The role references template files (httpd.conf.j2, vhost.conf.j2) that don't exist in the repository, causing task failures
- **Missing includes**: Tasks include docker_setup.yml which doesn't exist, breaking conditional Docker installation
- **Deprecated modules**: Uses deprecated `yum` module instead of `ansible.builtin.package` or `ansible.builtin.dnf`
- **Deprecated loops**: Uses `with_items` instead of modern `loop` syntax
- **Firewall management**: Uses shell commands instead of proper firewalld module
- **Minimum Ansible version**: Targets very old Ansible 2.4, needs update to support modern features

### Migration Order
1. **Update syntax and modules** (low risk, high value)
   - Replace deprecated sudo with become
   - Update yum to dnf/package module
   - Convert with_items to loop syntax
   - Update minimum Ansible version requirement

2. **Fix missing dependencies** (moderate complexity)
   - Create missing template files (httpd.conf.j2, vhost.conf.j2)
   - Create docker_setup.yml task file or inline Docker tasks
   - Add proper error handling for missing files

3. **Security and best practices** (high complexity)
   - Replace shell commands with proper modules (firewalld)
   - Add variable validation and type checking
   - Implement proper secret management patterns
   - Add comprehensive error handling and idempotency checks

### Assumptions
- The role is intended for Apache HTTP server deployment on RHEL-family systems
- SSL certificates are managed externally (no certificate provisioning logic present)
- Docker installation is optional and used primarily for monitoring (node-exporter)
- The role targets development/testing environments given the "QE Test" author attribution
- Missing template files contain standard Apache configurations
- The role should maintain backward compatibility with existing deployments
- Firewall rules are intended to be persistent across reboots
- PHP-MySQL integration suggests web application hosting requirements
- Virtual host configuration follows standard Apache practices
- Monitoring integration is optional and uses Prometheus ecosystem tools