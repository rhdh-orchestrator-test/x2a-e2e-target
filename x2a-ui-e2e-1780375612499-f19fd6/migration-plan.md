# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is or incorporated into Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for Python-based testing
  - Option 2: Ansible Test for native Ansible testing capabilities
  - Option 3: Continue using InSpec but invoke it from Ansible rather than Chef

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Ansible Test for more comprehensive testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for CI/CD pipeline integration

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible roles
  
- **SSH Hardening**: The SSH security controls in ssh_profile.rb need to be implemented in Ansible
  - Approach: Create an Ansible role for SSH hardening with the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely through Ansible Vault or external certificate management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule with Testinfra which provides similar testing capabilities
  - Create a mapping document for InSpec resources to Testinfra/Molecule equivalents

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform equivalent setup tasks
  - Consider using Ansible to deploy AWX or Ansible Automation Platform instead of Chef Automate

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need organization into proper roles and structure
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing frameworks
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The existing Ansible playbooks are functional and follow best practices
2. The InSpec tests are currently being used for compliance validation
3. There is no dependency on Chef-specific features that cannot be replicated in Ansible
4. The deployment scripts are used for setting up infrastructure and not for application deployment
5. There are no external dependencies or integrations not visible in the provided files
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The self-signed certificates are acceptable for the environment (not production)
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only