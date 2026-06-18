# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The migration will primarily involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef-specific components.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or other compliance tools

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS settings are maintained during migration.
  - Migration approach: Preserve the SSL configuration in the Ansible playbooks, which are already well-structured.

- **SSH Security Controls**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule verifiers.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex testing scenarios.

- **Chef Automate/Server Deployment**: Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible.
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower for similar functionality.

### Migration Order

1. **InSpec Tests** (low risk, high value): Convert InSpec tests to Ansible assertions or Molecule tests
2. **Chef Deployment Scripts** (moderate complexity): Convert bash scripts to Ansible playbooks for Chef deployment

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining the existing Ansible playbooks.
2. The Chef Automate and Chef Infra Server deployment scripts are still needed in the migrated solution.
3. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
4. No external dependencies or complex Chef cookbooks are present in the repository.
5. The migration is primarily focused on testing methodology rather than application deployment.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.