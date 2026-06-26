# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security compliance

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using Ansible's built-in `--check` mode with custom reporting

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Download and install required packages
  - Configure users and organizations if needed

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
  
- **SSH Security**: The SSH root login compliance check must be preserved in the Ansible-native testing solution.

- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing a more robust certificate management solution in the Ansible migration.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules. The compliance metadata (tags, impact, etc.) will need to be preserved in documentation or custom Ansible structures.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules and develop custom reporting for compliance metadata.

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that may not be directly available in Ansible.
  - Mitigation: Consider integrating with tools like Ansible Tower/AWX for reporting or develop custom reporting scripts.

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **chef-automate-deploy** and **chef-server-deploy** (convert bash scripts to Ansible playbooks)
4. **website_https_verify.rb** and **ssh_profile.rb** (convert InSpec tests to Ansible-native testing)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need significant changes.
3. There's no requirement to maintain backward compatibility with Chef InSpec after migration.
4. The deployment scripts for Chef Automate and Chef Infra Server will be replaced entirely, as these tools won't be needed in an Ansible-only environment.
5. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
6. The security compliance requirements (STIG references, CCI identifiers) need to be preserved in the new implementation.
7. The current implementation is for demonstration/testing purposes and may need additional hardening for production use.