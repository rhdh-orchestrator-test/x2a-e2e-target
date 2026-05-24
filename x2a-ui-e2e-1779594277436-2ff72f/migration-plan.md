# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
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
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file for the web server. Can be preserved as-is or converted to a template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Use TestInfra (Python-based testing framework that works well with Ansible)

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Consider using ansible-navigator for local development

### Security Considerations

- **SSL Configuration**: The playbooks already handle SSL security properly by disabling SSLv3 and enabling only TLSv1.2. This should be preserved in the migration.

- **SSH Security**: The SSH security tests check for root login restrictions. Ensure these checks are maintained in the new testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly, which is acceptable for testing but should be replaced with proper certificate management for production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the equivalent assertions and checks. TestInfra provides similar functionality to InSpec and may be the easiest migration path.

- **Chef Automate/Server Setup**: Converting the Chef server setup scripts to Ansible will require understanding the equivalent Ansible Tower/AWX setup process. This may involve multiple roles and potentially external collections.

### Migration Order

1. **InSpec Tests** (Priority 1): Convert the InSpec tests to Ansible-native testing solutions first, as they are critical for verifying the functionality of the playbooks.
   
2. **Test Kitchen Configuration** (Priority 2): Replace or update the Test Kitchen configuration to work with the new testing framework.

3. **Chef Automate/Server Setup Scripts** (Priority 3): Convert these to Ansible playbooks last, as they are separate from the main functionality.

### Assumptions

1. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are working correctly and do not need significant changes beyond potential refactoring for best practices.

2. The primary goal is to replace Chef InSpec testing with Ansible-native testing while maintaining the same level of compliance verification.

3. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description.

4. The Chef Automate and Chef Infra Server setup scripts are intended to be replaced with equivalent Ansible automation for setting up a centralized management platform.

5. No external Chef cookbooks or complex Chef-specific features are in use that would require special handling during migration.