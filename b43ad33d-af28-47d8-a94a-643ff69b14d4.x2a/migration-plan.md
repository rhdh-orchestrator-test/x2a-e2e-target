# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security compliance
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website with Apache. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible-native testing framework or adapting to use Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations include replacing with Ansible role for deploying alternative compliance platforms.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible role for configuration management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a standalone testing tool integrated with Ansible workflows
- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
- **Chef Automate**: Replace with alternative compliance platforms like Ansible Tower/AWX with compliance scanning capabilities
- **Chef Infra Server**: Replace with Ansible-based configuration management approach

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL security hardening present in the poodle_fix.yml playbook
  - Migration approach: Convert to Ansible role with appropriate SSL hardening tasks
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Create Ansible role for certificate management with options for self-signed or proper CA certificates
- **SSH Security**: The ssh_profile.rb InSpec test enforces SSH security compliance
  - Migration approach: Create Ansible role for SSH hardening with appropriate compliance checks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The repository demonstrates using Chef InSpec for compliance testing with Ansible
  - Mitigation strategy: Either maintain InSpec as a compliance tool or migrate to Ansible-native compliance solutions
- **Integration Testing**: The repository uses Test Kitchen for integration testing
  - Mitigation strategy: Replace with Molecule for Ansible-native integration testing

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Compliance Testing** (Moderate complexity)
   - Convert InSpec tests to Ansible-native testing or maintain as separate compliance layer

3. **Chef Deployment Scripts** (High complexity)
   - Replace Chef Automate and Chef Infra Server deployment scripts with Ansible roles for alternative solutions

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec for compliance testing alongside Ansible, not for production deployment
2. The Chef components (Automate, Infra Server) are being used primarily for compliance capabilities
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The security requirements (SSL configuration, SSH hardening) must be maintained in the migration
5. The migration will consolidate on Ansible while potentially maintaining InSpec for compliance testing if needed