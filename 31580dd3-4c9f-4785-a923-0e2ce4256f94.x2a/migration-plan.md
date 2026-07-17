# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Chef server deployment scripts focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** as most of the content is already in Ansible format, with the primary focus being on converting InSpec tests to Ansible-compatible testing frameworks and replacing the Chef server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a single engineer to complete the migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and InSpec tests for configuring and validating HTTPS websites
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache configuration, SSL certificate generation, compliance testing

- **setup-automate**:
    - Description: Directory containing shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

- **chef-and-ansible/tests**:
    - Description: Directory containing Chef InSpec test profiles for validating configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS website validation, SSH security validation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2.
- `chef-and-ansible/index.html`: Sample HTML file used for testing. No migration needed, can be used as-is.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests for validating HTTPS website configuration.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for validating SSH security configurations.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying only Chef Infra Server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen with Vagrant**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture:
  - Maintain TLSv1.2 requirement
  - Consider upgrading to TLSv1.3 where supported
  - Ensure proper certificate handling

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure this security check is maintained in the Ansible implementation.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated during playbook execution, no pre-existing secrets detected

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible assertions or Molecule verifiers.

- **Chef Server Deployment**: Replacing the Chef server deployment scripts with Ansible playbooks.
  - Mitigation: Research existing Ansible roles for Chef server deployment or create new roles based on the installation steps in the scripts.

### Migration Order

1. **chef-and-ansible/website_https.yml** (already in Ansible format, low risk)
2. **chef-and-ansible/poodle_fix.yml** (already in Ansible format, low risk)
3. **chef-and-ansible/tests/website_https_verify.rb** (convert to Ansible testing framework, moderate complexity)
4. **chef-and-ansible/tests/ssh_profile.rb** (convert to Ansible testing framework, moderate complexity)
5. **setup-automate/deploy-automate.sh** and **setup-automate/deploy-chef-server.sh** (convert bash scripts to Ansible playbooks, higher complexity)

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use.
2. The InSpec tests are intended to validate the configurations applied by the Ansible playbooks.
3. The Chef server deployment scripts are included as examples and may not be actively used in conjunction with the Ansible playbooks.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what is explicitly defined in the repository.
6. The migration goal is to standardize on Ansible while maintaining the same functionality and security posture.