# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks with a focus on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks and Chef InSpec tests for configuring and validating HTTPS websites
    - Path: chef-and-ansible
    - Technology: Ansible and Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Server installation, Chef Automate installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for remediating SSL POODLE vulnerability
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate with Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

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
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable protocols

- **SSH Security**: Maintain the SSH hardening requirements from the InSpec profile
  - Disable root login via SSH
  - Preserve compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely (currently generated on the fly)
  - Count of credentials detected: 
    - setup-automate: 2 hardcoded credentials (username, password)

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec with Ansible-native compliance testing
  - Solution: Use ansible-lint with custom rules or integrate with Ansible Automation Platform's compliance capabilities

- **Chef Server Deployment**: The Chef server deployment scripts need to be eliminated as part of the migration
  - Solution: Replace with Ansible roles for managing the infrastructure that was previously managed by Chef

### Migration Order

1. **chef-and-ansible** (low risk, already in Ansible)
   - Refactor playbooks into proper Ansible role structure
   - Add documentation

2. **chef-and-ansible/tests** (moderate complexity)
   - Convert InSpec tests to equivalent Ansible assertions or ansible-lint rules
   - Ensure all compliance checks are preserved

3. **setup-automate** (high complexity)
   - Determine if Chef Server is still needed after migration
   - If not, document decommissioning process
   - If yes, create Ansible playbook to deploy and configure Chef Server

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than to provide production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There is no actual dependency on Chef Infra Server for the Ansible playbooks to function
4. The security compliance requirements (e.g., STIG standards referenced in the SSH profile) must be maintained
5. Test Kitchen is used primarily for development and testing, not for production deployments