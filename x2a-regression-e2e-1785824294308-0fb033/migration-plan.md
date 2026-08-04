# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used as a template for website deployment. Can be converted to an Ansible template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Replace with Ansible Molecule
  - For compliance testing: Replace with ansible-lint or integrate with OpenSCAP

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Consider replacing with:
  - AWX/Ansible Tower for orchestration
  - Ansible Content Collections for configuration management
  - Compliance as Code frameworks like OpenSCAP or DISA STIG Ansible roles

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with proper variable parameterization

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be implemented in Ansible
  - Approach: Create an Ansible role for SSH hardening with appropriate variables

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely using Ansible Vault or external certificate management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks
  - Mitigation: Use Ansible assert modules and Molecule for functional testing, consider OpenSCAP for compliance testing

- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem
  - Mitigation: Evaluate AWX/Tower for orchestration and reporting, consider complementary tools for compliance reporting

### Migration Order

1. **website_https.yml** (Priority 1): Convert to an Ansible role with proper variable parameterization (low risk, high value)
2. **poodle_fix.yml** (Priority 1): Integrate into the website_https role as a security hardening task (low risk)
3. **InSpec Tests** (Priority 2): Convert to Ansible Molecule tests (moderate complexity)
4. **Chef Deployment Scripts** (Priority 3): Replace with Ansible playbooks for deploying alternative orchestration solutions (high complexity)

### Assumptions

1. The current Ansible playbooks are relatively simple and don't use complex Ansible features or integrations
2. The InSpec tests are primarily used for validation and not integrated into a larger compliance framework
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a management environment, which will need an equivalent in the Ansible ecosystem
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. There are no external dependencies or integrations not visible in the provided code
6. The migration will maintain the same level of security hardening and compliance validation
7. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling