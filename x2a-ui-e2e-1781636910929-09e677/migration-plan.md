# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that need to be converted to Ansible playbooks.

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing
  - Alternatively, use ansible-test for integration testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security in the Apache configuration

- **SSH Security**: The SSH root login check must be preserved in the Ansible testing framework
  - Convert the InSpec control to an equivalent Ansible assertion or Molecule verification

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 3 credentials detected (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing requires careful mapping of assertions
  - Mitigation: Use Molecule's verifier plugins or custom verification playbooks to replicate InSpec functionality

- **Compliance Metadata**: The InSpec tests contain compliance metadata (STIG IDs, CCI references) that needs to be preserved
  - Mitigation: Document these in Ansible playbook comments or create a separate compliance mapping document

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible requires understanding of Chef Server architecture
  - Mitigation: Create Ansible roles for Chef Server deployment or consider if Chef Server is still needed after migration

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, but should be reviewed and optimized for current Ansible best practices

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, but should be reviewed and optimized for current Ansible best practices

3. **website_https_verify.rb** (moderate complexity)
   - Convert InSpec tests to Molecule verification or custom Ansible assertions

4. **ssh_profile.rb** (moderate complexity)
   - Convert InSpec control to Ansible security check, preserving compliance metadata

5. **Chef deployment scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks for Chef Automate and Chef Server deployment
   - Consider if these components are still needed in the new architecture

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and don't require significant changes.

2. The primary goal is to replace Chef InSpec testing with Ansible-native testing while maintaining the same level of compliance validation.

3. The Chef Automate and Chef Server deployment scripts may not be needed if the migration is moving away from Chef entirely.

4. The target environment will continue to be Ubuntu 20.04 or compatible systems.

5. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests must be preserved in the Ansible solution.

6. Test Kitchen is currently used for test orchestration and will need to be replaced with an Ansible-native solution.

7. The repository appears to be a demonstration or example repository rather than a production system, based on the README content.