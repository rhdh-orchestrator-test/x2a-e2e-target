# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, with minimal complexity due to the small codebase and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
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
- `index.html`: Simple HTML file used as a template for the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly defined in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible Assert module for in-playbook validation
  - Option 3: Ansible-lint for static analysis

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that configure equivalent functionality:
  - For compliance scanning: AWX/Tower with custom scan playbooks
  - For configuration management: AWX/Tower for orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Maintain the same configuration parameters in the Ansible playbooks

- **SSH Hardening**: The SSH root login check must be preserved
  - Migration approach: Convert the InSpec control to an Ansible playbook that checks and enforces the same policy

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

- **Self-signed certificates**: The playbook generates self-signed certificates
  - Migration approach: Maintain the same approach or consider integrating with Let's Encrypt for production environments

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Use Ansible's assert module with uri module for HTTP checks and command module with regex for SSL validation

- **Compliance Reporting**: InSpec provides structured compliance reporting
  - Mitigation: Implement custom reporting using Ansible callback plugins or integrate with AWX/Tower reporting

- **Chef Server Functionality**: Replacing Chef Server management capabilities
  - Mitigation: AWX/Tower can provide similar functionality for managing configurations across nodes

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible playbooks
4. **Test Kitchen Configuration** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance validation
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications
3. There is no requirement to maintain backward compatibility with Chef tools
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The deployment is for testing/demonstration purposes as indicated by the self-signed certificates and simple configurations
6. The hardcoded credentials in the deployment scripts are not used in production environments
7. There are no external integrations or dependencies not visible in the provided files