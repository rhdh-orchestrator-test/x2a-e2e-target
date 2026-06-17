# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring the existing Ansible playbooks follow best practices

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Can be kept as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using ansible-test for unit testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS protocols are enforced in the migrated solution.
  - Migration approach: Maintain the same SSL hardening but use Ansible's more modern modules and follow current best practices.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule verifiers.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use a combination of Ansible's assert module and custom modules where needed.

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible.
  - Mitigation: Create an Ansible role that performs the same system configurations and installations.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need to be reorganized into roles and follow best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, need to be converted to Ansible-native testing.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, need to be completely rewritten as Ansible playbooks.

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining the same level of compliance verification.
2. The existing Ansible playbooks are functional but may need restructuring to follow Ansible best practices.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with Ansible playbooks that deploy alternative solutions or the same Chef products.
4. The target environment will remain Ubuntu 20.04 or be updated to a newer Ubuntu LTS release.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.
6. The Test Kitchen configuration is used primarily for development and testing, not for production deployments.