# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a test page. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX or Ansible Tower for enterprise management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the Apache SSL configuration remains compliant with security best practices

- **SSH Security**: The SSH root login check must be preserved
  - Approach: Convert the InSpec control to an Ansible task that validates the same configuration

- **Self-signed Certificates**: The playbook generates self-signed certificates
  - Approach: Maintain this functionality but consider adding a note about using proper certificates in production

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions
  - Mitigation: Use Ansible's assert module with appropriate conditions to match InSpec expectations
  - For complex validations, consider using the uri module to test HTTP responses

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for AWX/Tower deployment that provide similar functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks for AWX/Tower deployment
4. **Test Infrastructure** (kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance validation
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The deployment scripts are currently used for setting up a test/development environment, not production
5. There is no integration with external systems beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are not used in production environments
7. The self-signed certificates are acceptable for the current use case
8. There are no additional Chef cookbooks or resources being used beyond what's visible in the repository