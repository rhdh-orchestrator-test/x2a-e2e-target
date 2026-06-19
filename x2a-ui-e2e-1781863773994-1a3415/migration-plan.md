# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Addressing the Chef Automate and Chef Infra Server deployment scripts

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef InSpec and Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
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
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance check

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
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Implement custom testing using Ansible assert modules

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative compliance solutions:
  - Option 1: Migrate to Ansible Automation Platform for centralized management
  - Option 2: Use OpenSCAP with Ansible for compliance scanning
  - Option 3: Implement GitLab CI/CD or Jenkins for automation pipelines

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the POODLE fix playbook
  - Migration approach: Preserve the same SSL protocol restrictions in the Ansible tasks

- **SSH Hardening**: The SSH compliance checks must be maintained
  - Migration approach: Convert InSpec SSH tests to Ansible assert tasks or Molecule/Testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Testinfra with Molecule which provides a similar testing experience to InSpec

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting using Ansible's json_query and template modules, or integrate with tools like OpenSCAP

- **Test Kitchen to Molecule**: Test Kitchen configuration needs to be converted to Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Only need minor adjustments for best practices and integration with testing framework

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible-compatible testing framework

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Replace with Ansible roles for deploying alternative compliance solutions

### Assumptions

1. The primary purpose of this repository is for demonstration/example purposes rather than production use, as indicated by the README.md
2. The Chef InSpec tests are used for compliance verification of configurations managed by Ansible
3. The deployment scripts are used for setting up a test environment rather than production systems
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The migration will maintain the same level of compliance checking but using Ansible-native tools
6. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
7. There are no external dependencies or integrations beyond what's visible in the repository
8. The migration does not need to maintain backward compatibility with Chef InSpec