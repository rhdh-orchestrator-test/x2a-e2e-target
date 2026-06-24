# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring a web server with HTTPS
2. Chef InSpec tests for verifying compliance

Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration complexity is low to medium, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Replace InSpec tests with Ansible's built-in `assert` module or community modules like `ansible.builtin.uri` for HTTP checks
  - Consider using Ansible Lint for static analysis
  - For more complex compliance testing, consider integrating with OpenSCAP or using the `community.general.goss` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in `ansible-test` for integration testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for centralized automation
  - Ansible Galaxy for role sharing
  - GitLab CI/GitHub Actions for CI/CD pipelines

### Security Considerations

- **SSL Configuration**: The migration must maintain the same level of security by ensuring:
  - Proper SSL/TLS configuration in Apache (disabling SSLv3, enabling only TLSv1.2)
  - Secure certificate generation and management
  
- **SSH Security**: Maintain SSH hardening practices:
  - Disable root login
  - Implement proper authentication mechanisms

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks will require careful mapping of test functionality
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  
- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Integrate with tools like OpenSCAP or custom reporting solutions

- **Test Kitchen Workflow**: Current workflow uses Test Kitchen for orchestration
  - Mitigation: Implement equivalent workflow using Molecule or other Ansible-native testing tools

### Migration Order

1. **website-https playbook** (already in Ansible, low risk)
2. **poodle-fix playbook** (already in Ansible, low risk)
3. **InSpec tests** (medium complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires complete rewrite as Ansible playbooks)

### Assumptions

1. The current setup uses Test Kitchen primarily for testing Ansible playbooks, not Chef cookbooks
2. The InSpec tests are used for compliance verification of infrastructure provisioned by Ansible
3. The deployment scripts for Chef Automate and Chef Infra Server are used for setting up a separate Chef environment, not directly related to the Ansible playbooks
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. There are no additional Chef cookbooks or resources not visible in the provided repository structure
6. The migration aims to eliminate Chef dependencies entirely, including InSpec
7. The hardcoded credentials in the deployment scripts are for testing purposes only and will be properly secured in the migrated solution