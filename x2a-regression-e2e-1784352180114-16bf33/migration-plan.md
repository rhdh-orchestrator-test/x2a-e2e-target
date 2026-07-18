# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

This repository contains a mix of Chef deployment scripts and Ansible playbooks with Chef InSpec tests. The migration will focus on converting all components to pure Ansible while maintaining the security and compliance testing capabilities.

## Module Migration Plan

This repository contains Chef and Ansible technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring Apache HTTPS websites with InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by enforcing TLSv1.2 and disabling older protocols.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance checking.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Infra Server**: Replace with Ansible roles for configuration management
- **InSpec**: Either maintain as a compliance testing tool integrated with Ansible or replace with Ansible-native testing solutions like Ansible Molecule or ansible-lint

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook, ensuring TLSv1.2 is enforced and older protocols are disabled.
- **Certificate Management**: The self-signed certificate generation in website_https.yml must be properly migrated, potentially using Ansible's openssl modules.
- **SSH Security**: The SSH security compliance checks in ssh_profile.rb must be maintained, ensuring root login remains disabled.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL/TLS certificate references in the Apache configuration
  - Count of credentials detected: 3 (username, password, SSL certificates)

### Technical Challenges

- **InSpec Integration**: Determining whether to maintain InSpec for compliance testing or migrate to Ansible-native testing solutions. Mitigation strategy: Evaluate the complexity of the InSpec tests and determine if Ansible's built-in modules can provide equivalent functionality.
- **Chef Automate Replacement**: Identifying appropriate Ansible roles or collections to replace Chef Automate functionality. Mitigation strategy: Research community-maintained Ansible roles for infrastructure management or develop custom roles based on the Chef Automate deployment scripts.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk, already in Ansible format, may only need minor adjustments for consistency.
2. **Testing Framework** (chef-and-ansible/kitchen.yml, InSpec tests): Moderate complexity, requires deciding on testing approach and potentially converting InSpec tests to Ansible-native testing.
3. **Chef Deployment Scripts** (setup-automate/*.sh): High complexity, requires replacing Chef-specific deployment with Ansible roles and playbooks.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the chef-and-ansible/README.md.
2. The Chef deployment scripts are used for setting up a Chef infrastructure that may be used for other purposes not included in this repository.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The hardcoded credentials in the deployment scripts are examples and not used in production environments.
5. The InSpec tests are considered valuable and should be maintained in some form rather than completely replaced.
6. The migration should maintain the same level of security hardening present in the original configurations.