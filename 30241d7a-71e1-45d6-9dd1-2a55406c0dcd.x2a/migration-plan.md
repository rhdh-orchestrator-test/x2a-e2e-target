# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Consolidating the existing Ansible playbooks with the testing framework
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

Given the limited scope and the fact that most of the configuration is already in Ansible format, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef InSpec and Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in inventory management for multi-node testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible roles for infrastructure deployment
  - AWX/Ansible Tower for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (disabling SSLv3, enabling TLSv1.2)
  - Secure virtual host configuration

- **SSH Security**: The InSpec profile checks SSH root login configuration. Migration should:
  - Convert InSpec tests to Ansible assertions or Molecule tests
  - Maintain compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic.
  - Mitigation: Use Ansible's `assert` module with appropriate conditions or integrate with Molecule for more complex tests.

- **Test Kitchen to Molecule**: Test Kitchen's workflow differs from Molecule's, requiring adjustments to test execution.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration.

- **Chef Server Deployment**: The current deployment scripts use Chef-specific commands that need Ansible equivalents.
  - Mitigation: Research and implement Ansible roles that can deploy similar infrastructure or use container-based alternatives.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need integration with new testing framework.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Highest complexity, requiring complete rewrite as Ansible roles.

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing.
2. The existing Ansible playbooks are working correctly and don't need functional changes.
3. The deployment scripts are used for setting up test environments and not production infrastructure.
4. No external Chef cookbooks or complex Chef-specific features are in use beyond what's visible in the repository.
5. The team has expertise in both Chef InSpec and Ansible to facilitate the migration.
6. The security compliance requirements (referenced in the InSpec profiles) must be maintained in the Ansible solution.