# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity as most of the configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Sample HTML file used for testing - can be preserved as-is or incorporated into Ansible templates

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with testinfra for Python-based testing
  - Option 2: Ansible Molecule with Goss for YAML-based testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained during migration
  - Consider expanding the security hardening with additional modern TLS best practices

- **SSH Security**: The SSH security controls tested by the InSpec profile should be implemented in Ansible
  - Convert the InSpec SSH root login check to equivalent Ansible assertions
  - Preserve the STIG compliance metadata for audit purposes

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Testing Framework Transition**: Moving from Chef InSpec to an Ansible-native testing solution
  - Challenge: Preserving the same level of testing coverage and readability
  - Mitigation: Create a mapping between InSpec resources and the chosen testing framework's equivalent assertions

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Challenge: Most Ansible testing frameworks don't have built-in support for compliance metadata
  - Mitigation: Store compliance metadata in structured YAML files that can be referenced by tests

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts
  - Challenge: Determining if Chef Automate is still needed or if it should be replaced with an Ansible-native solution
  - Mitigation: Evaluate if Chef Automate's functionality is required or if it can be replaced with alternatives like AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **Testing Framework** - Set up Ansible Molecule or alternative testing framework
3. **InSpec Test Conversion** - Convert website_https_verify.rb and ssh_profile.rb to the chosen testing framework
4. **Chef Automate Scripts** - Convert the deployment scripts to Ansible playbooks

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while preserving the existing Ansible playbooks
2. The repository is primarily used for demonstration/educational purposes rather than production deployment
3. The Chef Automate and Chef Server deployment scripts are intended to be replaced with Ansible equivalents
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The security requirements (STIG compliance, SSL hardening) must be maintained in the migrated solution
6. Test Kitchen is only used for development/testing and not for production deployments