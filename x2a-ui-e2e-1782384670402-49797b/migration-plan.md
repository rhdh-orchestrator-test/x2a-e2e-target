# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing primarily on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that most of the infrastructure code is already in Ansible format.

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Migration consideration: Keep as-is or incorporate into Ansible templates.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for simpler test cases
  - Option 3: Convert InSpec tests to Ansible assert tasks for direct integration

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

- **Vagrant (latest)**: Can be retained for local development or replaced with containerized testing using Docker with Molecule

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables vulnerable SSL protocols
  - Migration approach: Maintain the same configuration in Ansible playbooks

- **SSH Security**: The SSH root login check in ssh_profile.rb must be preserved
  - Migration approach: Convert to Ansible assert tasks or Molecule with Testinfra

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated during deployment and don't require special handling

### Technical Challenges

- **Challenge 1**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule with Testinfra which has similar syntax and capabilities to InSpec

- **Challenge 2**: Replacing Chef Automate and Chef Infra Server deployment scripts
  - Mitigation: Create Ansible roles for configuration management without requiring Chef infrastructure

- **Challenge 3**: Ensuring compliance validation remains effective after migration
  - Mitigation: Implement comprehensive testing to verify that compliance checks are equivalent

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Only requires minor updates to follow best practices and integrate with new testing framework

2. **website_https_verify.rb** and **ssh_profile.rb** (moderate complexity)
   - Convert InSpec tests to Ansible Molecule with Testinfra or Goss

3. **chef-automate-deployment** and **chef-server-deployment** (high complexity)
   - Replace with Ansible roles for configuration management without Chef infrastructure

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.

2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and don't require significant changes beyond integration with a new testing framework.

3. The deployment scripts for Chef Automate and Chef Infra Server are used for setting up a testing environment and are not part of the core functionality being demonstrated.

4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

5. There are no external dependencies or integrations beyond what is explicitly defined in the repository.

6. The migration will focus on preserving the compliance automation functionality while eliminating the dependency on Chef InSpec.

7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution.