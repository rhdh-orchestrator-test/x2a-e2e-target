# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible-based deployment solutions.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the small codebase and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled according to security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with `ansible-test` for integration testing
  - Use Ansible's `assert` module for validation within playbooks
  - Consider Molecule for Ansible role testing
  - Alternative: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing and validation
  - Ansible's built-in inventory management for multi-node testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible roles for configuration management platform deployment
  - Consider migrating to AWX/Ansible Tower as a replacement for Chef Automate

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Maintain the same configuration parameters in the Ansible playbooks

- **SSH Security Controls**: The SSH root login verification must be preserved
  - Approach: Convert the InSpec control to an Ansible task that verifies the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's `assert` module with appropriate conditionals to achieve similar validation

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Consider integrating with tools like Ansible Tower/AWX for compliance reporting or use community modules for generating compliance reports

- **Test Kitchen Workflow**: The current workflow uses Test Kitchen to orchestrate testing
  - Mitigation: Implement similar workflow using Molecule or custom Ansible playbooks for test orchestration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible roles for platform deployment
4. **Test Kitchen Configuration** (kitchen.yml) - Replace with Molecule or custom test orchestration

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while preserving the security validation capabilities
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications
3. The deployment scripts for Chef Automate/Server are used for setting up a management platform that will be replaced by Ansible Tower/AWX or similar
4. No external data sources or complex integrations exist beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The security compliance requirements (STIG references) will remain the same after migration
7. No custom InSpec resources are being used that would require special handling during migration