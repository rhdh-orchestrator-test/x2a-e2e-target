# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate infrastructure configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests. The estimated timeline for migration would be 1-2 weeks, with low complexity for the Ansible playbooks (which can be kept as-is) and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance solutions like OpenSCAP
  - Option 2: Deploy Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Proper SSL protocol settings (TLSv1.2 enforcement)
  - Disabling vulnerable protocols (SSL3)

- **SSH Security**: The InSpec profile checks SSH root login settings. Migration should:
  - Convert InSpec checks to Ansible assertions or molecule tests
  - Maintain compliance with security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require:
  - Understanding the InSpec resource models (port, http, ssl, sshd_config)
  - Creating equivalent assertions in Ansible or Molecule
  - Maintaining compliance metadata (STIG IDs, CCI numbers)

- **Chef Server Deployment**: If Chef Server functionality is still needed:
  - Determine if Chef Server is required or if Ansible can fully replace it
  - If needed, create Ansible playbooks to deploy Chef Server with proper configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, can be kept as-is
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks if the functionality is still needed

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks can be kept largely as-is
3. Test Kitchen is used only for development/testing and not in production
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments
5. No actual Chef cookbooks or recipes are present in the repository
6. The repository is primarily for demonstration purposes rather than production use