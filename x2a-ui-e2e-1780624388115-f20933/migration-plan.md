# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Preserving the existing Ansible playbooks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache (POODLE)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with TestInfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Integrate with pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system requirements (hostname, sysctl parameters)
  - Deploy alternative compliance platforms (options include:)
    - AWX/Ansible Tower for automation
    - Compliance as Code using OpenSCAP with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Maintain the same SSL protocol restrictions in the Ansible playbooks

- **SSH Hardening**: The SSH compliance tests must be migrated to equivalent Ansible tests
  - Approach: Convert InSpec SSH tests to Ansible assert tasks or TestInfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, possibly using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's Ruby-based tests to Ansible's YAML format or TestInfra
  - Mitigation: Create a mapping of InSpec resources to TestInfra or Ansible assert modules
  - Example: InSpec's `describe port(443)` becomes TestInfra's `host.socket("tcp://0.0.0.0:443").is_listening`

- **Chef Server Functionality**: Replacing Chef Server user/org management
  - Mitigation: Implement equivalent user management in Ansible, possibly using AWX/Tower for organization management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity to convert to Ansible-compatible tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires architectural decisions

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't need functional changes
3. There's no requirement to maintain backward compatibility with Chef Automate/Server
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives