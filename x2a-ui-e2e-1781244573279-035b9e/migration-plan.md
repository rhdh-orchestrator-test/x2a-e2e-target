# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible Assert module for inline testing
  - Option 3: Ansible-lint for static analysis

- **Test Kitchen**: Replace with:
  - Ansible Molecule for test orchestration
  - Alternatively, maintain Test Kitchen but use the Ansible verifier instead of InSpec

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Configure hostname
  - Deploy alternative compliance solutions (options below)

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain handler for restarting services after configuration changes

- **SSH Hardening**: The SSH root login check must be preserved
  - Convert InSpec control to Ansible assert or use ansible-lint security rules
  - Maintain compliance metadata (STIG IDs, CCI references)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use Ansible assert module with appropriate conditionals or Molecule verifiers

- **Compliance Reporting**: Chef InSpec provides built-in compliance reporting
  - Challenge: Replicating compliance reporting capabilities in Ansible
  - Mitigation: Consider integrating with tools like OpenSCAP, Ansible Tower/AWX, or compliance as code solutions

- **Chef Automate Replacement**: Finding equivalent functionality
  - Challenge: Chef Automate provides integrated compliance scanning and reporting
  - Mitigation: Consider AWX/Tower with compliance scanning plugins or standalone compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible playbooks and implement alternative compliance solution

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining compliance capabilities
2. The existing Ansible playbooks are functioning correctly and only need minimal adjustments
3. Test Kitchen can be replaced with Ansible Molecule or similar testing framework
4. The deployment scripts are used for setting up a compliance environment that will need an alternative solution
5. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
6. No external dependencies or integrations beyond what's visible in the repository
7. The hardcoded credentials in deployment scripts are for demonstration purposes only
8. The compliance requirements (STIG references) in ssh_profile.rb need to be maintained in the new solution