# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing where appropriate
  - For compliance testing specifically, consider migrating to OpenSCAP with ansible-role-compliance

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the migrated solution
  - Verify that only TLSv1.2 is enabled and SSLv3 is disabled

- **SSH Security**: Maintain the SSH root login restrictions verified by the ssh_profile.rb test
  - Convert the InSpec control to an equivalent Ansible assertion or Molecule test
  - Preserve the STIG compliance references for documentation and audit purposes

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible/Molecule tests will require careful mapping of assertions
  - Challenge: InSpec has specific matchers for SSL/TLS protocols that may not have direct equivalents
  - Mitigation: May need to write custom Ansible modules or use shell commands with assertions

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Challenge: The scripts perform Chef-specific operations that need Ansible equivalents
  - Mitigation: Research Ansible roles for Chef deployment or create custom roles

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks
4. **Test Infrastructure** (kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. The existing Ansible playbooks are functioning correctly and don't require significant refactoring
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The deployment scripts are used for setting up test environments and not production systems (given the hardcoded credentials)
5. The migration is primarily focused on moving away from Chef InSpec while maintaining the existing Ansible functionality
6. No additional features or improvements are required beyond the direct migration
7. The security compliance requirements (STIG references) need to be preserved in the migrated solution