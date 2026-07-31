# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on using Chef InSpec for compliance testing alongside Ansible for configuration management. There are also setup scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:

1. Converting the Chef InSpec tests to Ansible-compatible testing frameworks
2. Replacing the Chef Automate and Chef Infra Server setup scripts with Ansible playbooks
3. Ensuring all compliance testing can be performed within the Ansible ecosystem

Estimated timeline: 1-2 weeks for a small team (1-2 engineers), with low complexity.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using a self-signed certificate
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in assert module for simple tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and job scheduling
  - Ansible Collections for content distribution
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS protocols are enforced in the migrated solution.
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2) in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint to verify SSH configuration.

- **Self-signed Certificates**: The playbook generates self-signed certificates.
  - Migration approach: Use Ansible's openssl_* modules (already in use) for certificate management.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible's assert module for simple tests, or integrate with Molecule for more comprehensive testing.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting capabilities.
  - Mitigation: Consider using Ansible Tower/AWX with custom reporting dashboards or integrate with third-party compliance tools.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. Only need to be reviewed and potentially optimized.

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-compatible testing frameworks.

3. **Chef Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for deploying alternative orchestration platforms.

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use.

2. The InSpec tests are used for compliance verification of configurations managed by Ansible.

3. There may be additional Chef cookbooks or resources not present in this repository that are referenced or used in conjunction with these examples.

4. The migration goal is to have a fully Ansible-based solution without dependencies on Chef products.

5. The current setup uses Test Kitchen with Vagrant for local testing, which will need to be replaced with an Ansible-native testing solution.

6. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.