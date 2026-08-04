# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and integrating the Chef InSpec testing capabilities into the Ansible workflow. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and tests.

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
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Simple HTML file used as a template for website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for basic validation
  - Option 2: Integrate with Molecule for comprehensive testing
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks
  - Option 4: Keep InSpec as a testing tool but integrate it with Ansible CI/CD pipeline

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant-based testing scripts

- **Chef Automate/Server Deployment**: Convert to Ansible roles for:
  - Option 1: Deploy Chef Automate/Server using Ansible (if still needed)
  - Option 2: Replace Chef Automate/Server with Ansible AWX/Tower

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Disabling of vulnerable protocols (SSLv3)

- **SSH Hardening**: The InSpec tests verify SSH security. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Maintain compliance checks for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Use Ansible assert modules or integrate with a testing framework like Molecule

- **Maintaining Compliance Validation**: Ensuring security compliance checks are preserved
  - Mitigation: Create dedicated Ansible roles for compliance checking or integrate with compliance tools

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Add documentation and variables

2. **poodle_fix playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Consider merging with website_https as a security enhancement option

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-native testing or integrate with Molecule
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for infrastructure deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description.
2. The Chef InSpec tests are used for compliance validation of Ansible-managed systems.
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced with Ansible Tower/AWX.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing.
5. No external dependencies or complex infrastructure are involved beyond what's visible in the repository.
6. The migration will maintain the same level of security validation currently provided by InSpec tests.