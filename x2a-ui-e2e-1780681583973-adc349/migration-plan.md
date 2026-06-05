# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing primarily on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some Ansible code already exists.

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
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing the web server deployment

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Use community.general.inspec module to continue using InSpec tests with Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Preserve the existing Ansible task that enforces TLSv1.2 and disables older protocols

- **SSH Security**: The SSH root login compliance check must be maintained
  - Approach: Convert the InSpec control to an Ansible task that verifies the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use the community.general.inspec Ansible module as an interim solution while gradually migrating tests

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Implement compliance reporting using Ansible Automation Platform or integrate with tools like Prometheus/Grafana

- **Test Kitchen Integration**: Replacing the Test Kitchen workflow
  - Mitigation: Implement equivalent testing workflow using Ansible Molecule

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef Automate/Server with Ansible Automation Platform or equivalent

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and follow best practices
2. The InSpec tests are currently used for compliance validation of infrastructure configured by Ansible
3. The repository is primarily for demonstration purposes as indicated by the README.md
4. The Chef Automate and Chef Server deployment scripts are used for setting up a test environment
5. No actual Chef cookbooks or recipes are present in the repository that need migration
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The migration will maintain the same level of security compliance checking
8. No external dependencies or integrations beyond what's visible in the repository