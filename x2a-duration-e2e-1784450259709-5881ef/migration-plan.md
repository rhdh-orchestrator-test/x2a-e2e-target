# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and SSL, with Chef InSpec tests for compliance verification
    - Path: chef-and-ansible (verified directory exists)
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing
    - Files: website_https.yml, poodle_fix.yml, kitchen.yml, tests/website_https_verify.rb, tests/ssh_profile.rb

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate (verified directory exists)
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup
    - Files: deploy-automate.sh, deploy-chef-server.sh

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates. Migration considerations include preserving the SSL configuration and virtual host setup.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2. Migration considerations include ensuring this security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with equivalent Ansible testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure setup.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Replace with Ansible-native testing using ansible-test or Molecule
  2. Maintain InSpec as a compliance tool but invoke it from Ansible
  3. Replace with alternative compliance tools like Ansible Lint or OpenSCAP

- **Test Kitchen**: Currently used for testing Ansible playbooks. Replace with:
  1. Molecule for Ansible role and playbook testing
  2. Ansible-test for more comprehensive testing

- **Chef Automate/Infra Server**: Currently deployed via shell scripts. Replace with:
  1. Ansible playbooks to deploy alternative infrastructure management tools
  2. Consider migrating to AWX/Ansible Tower for similar functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration must maintain:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Secure virtual host configuration

- **SSH Hardening**: InSpec tests verify SSH security configurations. Migration must:
  - Maintain SSH security checks
  - Ensure root login remains disabled
  - Preserve compliance with security benchmarks (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates and keys generated and stored in `/etc/apache2/certs/`
  - Recommend implementing Ansible Vault for credential storage

### Technical Challenges

- **Compliance Testing**: The repository demonstrates Chef InSpec for compliance testing with Ansible. Migration options:
  1. **Challenge**: Maintaining compliance testing capabilities
     **Mitigation**: Either continue using InSpec with Ansible or migrate to Ansible-native compliance tools

- **Infrastructure Deployment**: The shell scripts deploy Chef infrastructure components.
  1. **Challenge**: Replacing Chef infrastructure components
     **Mitigation**: Develop Ansible playbooks for infrastructure management or migrate to AWX/Ansible Tower

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml) - Low risk, direct conversion to updated Ansible syntax
2. **Deployment Scripts** (setup-automate/*.sh) - Moderate complexity, requires replacing Chef infrastructure
3. **Compliance Tests** (chef-and-ansible/tests/*.rb) - Higher complexity, requires decision on compliance strategy

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements (STIG/CIS benchmarks referenced in InSpec tests) must be maintained
5. The repository is primarily for demonstration/educational purposes as indicated by the README
6. No external data sources or complex state management is required
7. The Apache configuration and SSL hardening are the primary infrastructure components to preserve