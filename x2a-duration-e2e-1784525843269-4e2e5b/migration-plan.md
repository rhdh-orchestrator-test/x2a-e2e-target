# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks, and integrating the existing InSpec tests into an Ansible-based compliance workflow.

Estimated timeline: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible Molecule or maintaining Test Kitchen for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration considerations include integrating with Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations include maintaining compliance checks in the new Ansible structure.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations include replacing with Ansible roles for configuration management platform deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for configuration management platform deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package management in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment or integrate with AWX/Ansible Tower
- **Chef Infra Server**: Replace with Ansible roles for configuration management platform deployment or integrate with AWX/Ansible Tower
- **InSpec**: Maintain InSpec for compliance testing but integrate with Ansible workflows, or replace with Ansible-native solutions like ansible-lint and Molecule

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook, ensuring TLSv1.2 is enforced and vulnerable protocols are disabled.
- **SSH Security**: The SSH security profile in ssh_profile.rb must be maintained in the Ansible migration, ensuring root login remains disabled.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **InSpec Integration**: Determining how to maintain compliance testing with InSpec while migrating to a pure Ansible workflow. Mitigation: Use Ansible's built-in testing capabilities or maintain InSpec as a separate compliance tool.
- **Chef Automate Replacement**: Deciding whether to replace Chef Automate with Ansible Tower/AWX or another solution. Mitigation: Evaluate requirements and determine if Ansible Tower/AWX meets the needs or if another solution is required.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk, already in Ansible format, just need to be reorganized into Ansible roles and playbooks.
2. **InSpec Tests** (chef-and-ansible/tests): Moderate complexity, need to be integrated with Ansible testing framework or maintained as separate compliance tests.
3. **Chef Deployment Scripts** (setup-automate): High complexity, need to be replaced with Ansible roles for deploying configuration management platform.

### Assumptions

1. The current setup uses Chef Automate and Chef Infra Server for configuration management, with Ansible playbooks for specific tasks.
2. InSpec is used for compliance testing and will continue to be used in the migrated solution.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The migration will consolidate all configuration management under Ansible, replacing Chef components.
5. The hardcoded credentials in the deployment scripts are for testing purposes and will be replaced with secure credential management in the migrated solution.
6. The Apache HTTPS configuration is a critical component that must be maintained with the same security settings in the migrated solution.