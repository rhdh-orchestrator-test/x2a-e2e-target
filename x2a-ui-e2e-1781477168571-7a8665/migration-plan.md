# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

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
    - Description: Chef InSpec test that verifies SSH root login is disabled (security compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration considerations needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for testing Ansible roles and playbooks
  - Option 4: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solutions:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain the security hardening that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The InSpec tests verify SSH security configurations. Migration should include equivalent checks using Ansible.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely in the migrated solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks may require additional logic and different syntax.
  - Mitigation: Create custom Ansible modules or use the assert module with appropriate conditions.

- **Chef Automate Functionality**: If the team relies on Chef Automate features, equivalent functionality needs to be identified in Ansible ecosystem.
  - Mitigation: Map Chef Automate features to Ansible Automation Platform or AWX/Tower features.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing or integrate InSpec with Ansible
4. **Chef Deployment Scripts** (high complexity): Replace with Ansible playbooks for deploying Ansible management infrastructure

### Assumptions

1. The primary use case is compliance testing of infrastructure configured with Ansible.
2. The Chef InSpec tests are used for validation rather than configuration management.
3. There is no complex Chef cookbook logic that needs to be migrated, only InSpec tests.
4. The deployment scripts are used for setting up a test environment rather than production infrastructure.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The team is familiar with both Chef InSpec and Ansible, making the transition smoother.
7. There are no external dependencies or integrations not visible in the repository.
8. The hardcoded credentials in the deployment scripts are for testing purposes only.