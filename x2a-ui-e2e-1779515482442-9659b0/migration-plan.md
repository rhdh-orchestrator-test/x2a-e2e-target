# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on using Chef InSpec for compliance testing alongside Ansible for configuration management. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most of the Ansible components already in place. The migration will primarily involve converting the Chef InSpec tests to Ansible-native solutions and replacing the Chef server deployment scripts with Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already)
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already)
    - Key Features: Disables SSLv3, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing web server configuration. Can be reused as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Ansible assert module for runtime validation
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with other compliance tools like OSCAP

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Install and configure alternative compliance and automation platforms:
    - AWX/Ansible Tower for automation
    - Compliance solutions like OpenSCAP or Ansible Automation Platform

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security in Apache configuration

- **SSH Security**: The SSH root login compliance check must be preserved
  - Convert the InSpec control to Ansible assertions or checks
  - Maintain STIG compliance references and documentation

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native solutions while maintaining the same level of compliance validation
  - Mitigation: Use Ansible assert module with detailed conditions that match InSpec tests
  - Consider using ansible.posix and ansible.builtin modules for system checks

- **Test Framework**: Replacing Test Kitchen with an Ansible-native testing framework
  - Mitigation: Implement Molecule testing with the same platforms and verification steps

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality
  - Mitigation: Evaluate if a central server is needed or if Git-based Ansible can suffice
  - If centralized management is required, implement AWX/Ansible Tower

### Migration Order

1. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or Molecule tests (low risk, foundation for testing other components)
2. **Test Framework**: Replace kitchen.yml with Molecule configuration (moderate complexity, depends on test conversion)
3. **Chef Server Deployment Scripts**: Create Ansible playbooks to replace the bash scripts (higher complexity, requires decisions on architecture)

### Assumptions

1. The primary goal is to move all components to Ansible-native solutions
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) can be reused with minimal changes
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The deployment scripts are used for setting up test/development environments, not production
5. The hardcoded credentials in the deployment scripts are not used in production environments
6. The repository is primarily for demonstration purposes as indicated by the main README.md
7. The compliance requirements (STIG references) need to be maintained in the Ansible solution