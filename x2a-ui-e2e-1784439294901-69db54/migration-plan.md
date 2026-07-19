# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks with a focus on demonstrating compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and InSpec tests
    - Path: chef-and-ansible
    - Technology: Ansible and Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

- **chef-and-ansible/tests**:
    - Description: Directory containing Chef InSpec test profiles
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Website HTTPS verification, SSH security compliance testing

- **setup-automate**:
    - Description: Directory containing Chef Automate and Chef Server deployment scripts
    - Path: setup-automate
    - Technology: Shell scripts
    - Key Features: Chef Automate installation, Chef Infra Server installation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/website_https.yml`: Ansible playbook for HTTPS website configuration
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL hardening
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH compliance profile must be converted to Ansible
  - Create equivalent checks using ansible-lint rules
  - Implement SSH hardening using the community.general.ssh_config module

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Solution: Use Ansible assert module or custom modules for verification tasks
  - Alternative: Keep InSpec as a verification tool but invoke it from Ansible

- **Chef Automate Replacement**: Determining the appropriate Ansible alternative
  - Solution: Consider Ansible Automation Platform for enterprise features
  - Alternative: Use AWX (open-source upstream of Ansible Tower) for smaller deployments

### Migration Order

1. **chef-and-ansible playbooks** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbooks
   - Convert to Ansible role structure for better reusability
   - Consolidate website_https.yml and poodle_fix.yml into a single role

2. **chef-and-ansible/tests** (moderate complexity)
   - Convert to Ansible assertion tasks or maintain as InSpec but integrate with Ansible

3. **setup-automate scripts** (high complexity)
   - Replace with Ansible playbooks for deploying alternative compliance solutions

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation with Chef InSpec alongside Ansible, not to provide production-ready infrastructure.

2. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to cloud environments.

3. There is no complex data migration required as this appears to be a demonstration repository rather than a production environment.

4. The security compliance requirements (particularly the STIG references in the SSH profile) must be maintained in the migrated solution.

5. The current setup uses Test Kitchen for testing, which will need to be replaced with an Ansible-native testing framework.

6. The Chef Automate and Chef Infra Server deployment scripts are for demonstration purposes and may not need direct migration if an alternative compliance solution is chosen.