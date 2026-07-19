# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability. Migration considerations include ensuring the security fix is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec testing. Migration considerations include replacing with Ansible-native testing framework or adapting for pure Ansible testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Migration considerations include converting to Ansible-native testing or maintaining InSpec for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security. Migration considerations include converting to Ansible-native testing or maintaining InSpec for compliance testing.
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate. Migration considerations include replacing with Ansible playbook for infrastructure management.
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as a compliance testing tool or replace with Ansible-native alternatives:
  - Option 1: Keep InSpec for compliance testing, called from Ansible
  - Option 2: Replace with Ansible's assert module and custom modules
  - Option 3: Integrate with Ansible Lint or other Ansible-native testing frameworks

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for integration testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks:
  - Option 1: Create Ansible roles for infrastructure management
  - Option 2: Use existing Ansible Galaxy roles for similar functionality

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL security hardening present in the current playbooks:
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management
  - Preserve the POODLE vulnerability fix

- **SSH Security**: The SSH compliance tests check for root login restrictions:
  - Ensure Ansible playbooks enforce the same SSH security standards
  - Maintain compliance with security requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using Ansible Vault or integration with a secrets management system

### Technical Challenges

- **Compliance Testing Strategy**: Determining whether to maintain InSpec for compliance testing or migrate to Ansible-native testing:
  - Challenge: InSpec provides specialized compliance testing capabilities that may be difficult to replicate in Ansible
  - Mitigation: Consider a hybrid approach where Ansible handles configuration and InSpec handles compliance verification

- **Maintaining Security Standards**: Ensuring all security controls are properly implemented in the new Ansible code:
  - Challenge: Security controls are currently spread across playbooks and InSpec tests
  - Mitigation: Create a comprehensive security role in Ansible that implements all required controls

- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server deployment with equivalent functionality:
  - Challenge: Determining if Chef infrastructure is still needed or can be fully replaced
  - Mitigation: Evaluate current usage and decide whether to maintain Chef components for compliance or fully migrate to Ansible alternatives

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format):
   - `website_https.yml` - Convert to Ansible role with proper structure
   - `poodle_fix.yml` - Integrate into security hardening role

2. **Testing Framework** (Moderate complexity):
   - Replace Test Kitchen with Molecule or other Ansible testing framework
   - Decide on compliance testing strategy (keep InSpec or migrate)

3. **Infrastructure Deployment Scripts** (High complexity):
   - Convert Chef Automate/Infra Server deployment scripts to Ansible playbooks
   - Implement proper secret management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than for production use
2. The compliance testing functionality is a critical component that must be preserved
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Vagrant will continue to be used for development/testing environments
5. The security requirements specified in the InSpec profiles must be maintained
6. The repository does not contain actual application code, only infrastructure configuration
7. The Chef Automate and Chef Infra Server deployment scripts are for demonstration purposes and may not need to be fully migrated if the focus shifts to pure Ansible