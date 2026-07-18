# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing with InSpec

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration to mitigate POODLE vulnerability. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment management.
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment management.

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a complementary testing tool
- **Test Kitchen**: Replace with Ansible-native testing frameworks like Molecule
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management or alternative compliance tools

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for SSL/TLS protocols (specifically disabling SSLv3 and enabling TLSv1.2)
- **SSH Security**: The SSH compliance checks must be preserved in the Ansible implementation
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL keys)

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain Chef InSpec for compliance testing or migrate to Ansible-native testing solutions
- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server deployment with equivalent Ansible Tower/AWX deployment
- **Test Framework**: Replacing Test Kitchen with Ansible-native testing frameworks

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - moderate complexity, decide on testing strategy
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - high complexity, requires architectural decisions

### Assumptions

1. The primary purpose of this repository is demonstration/example code rather than production infrastructure
2. Chef InSpec is being used primarily for compliance testing alongside Ansible
3. The deployment scripts are for setting up Chef infrastructure, not for application deployment
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There is no complex state management or data persistence requirements
6. The migration goal is to standardize on Ansible while maintaining compliance testing capabilities
7. No external dependencies or third-party modules are being used beyond standard Ansible modules
8. The security configurations (SSL, SSH) are critical to maintain in the migration