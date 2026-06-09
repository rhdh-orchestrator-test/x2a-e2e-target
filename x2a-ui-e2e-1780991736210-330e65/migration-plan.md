# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (STIG)

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider OpenSCAP integration for compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Install and configure equivalent monitoring/compliance solutions
  - Options include:
    - AWX/Ansible Tower for automation
    - Prometheus/Grafana for monitoring
    - OpenSCAP for compliance

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml:
  - Disable SSLv3
  - Enable only TLSv1.2
  - Migration approach: Include these configurations in the Apache role

- **SSH Security**: Maintain SSH hardening requirements from ssh_profile.rb:
  - Disable root login
  - Migration approach: Include SSH hardening in a dedicated Ansible role

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native solutions while maintaining the same level of compliance verification
  - Mitigation: Research and implement equivalent testing mechanisms in Ansible, possibly using a combination of assert, command modules, and external tools

- **Certificate Management**: Ensuring proper SSL certificate generation and management
  - Mitigation: Use Ansible's openssl_* modules (already in use in the existing playbooks)

- **Idempotency**: Ensuring all scripts are converted to idempotent Ansible tasks
  - Mitigation: Careful review of bash scripts to identify state-changing operations and convert them to idempotent Ansible tasks

### Migration Order

1. **website_https.yml** (already in Ansible, low risk)
2. **poodle_fix.yml** (already in Ansible, low risk)
3. **InSpec Tests** (moderate complexity, convert to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, convert to Ansible playbooks)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The security requirements (SSL/SSH hardening) must be maintained in the migrated solution
4. The deployment scripts are examples and may need customization for actual production use
5. No external dependencies or integrations beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only