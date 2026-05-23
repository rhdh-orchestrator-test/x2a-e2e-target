# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a small set of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing primarily on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-verification**:
    - Description: InSpec tests for verifying HTTPS website deployment with proper SSL/TLS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content verification, SSL/TLS protocol security checks

- **ssh-security-profile**:
    - Description: InSpec compliance profile for SSH security configuration with STIG alignment
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, CCI compliance tagging, STIG alignment

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script with Chef CLI commands
    - Key Features: User creation, organization setup, system configuration

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script with Chef CLI commands
    - Key Features: User creation, organization setup, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `website_https.yml`: Ansible playbook for deploying a secure HTTPS website. No migration needed as this is already in Ansible format.
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. No migration needed as this is already in Ansible format.
- `index.html`: Simple HTML file used for website testing. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Lint for static code analysis
  - Option 2: Molecule for comprehensive testing
  - Option 3: Integration with other compliance tools like OSCAP or Compliance as Code

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure equivalent compliance scanning solutions
  - Set up centralized management if needed

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security posture of enforcing TLS 1.2 and disabling vulnerable protocols like SSL3.
  - Migration approach: Preserve the same security checks in Ansible-native testing

- **SSH Security Hardening**: The SSH compliance profile checks for secure SSH configuration.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule verifiers

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible's built-in modules (already in use)
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **Compliance Testing Framework**: InSpec provides a domain-specific language for compliance testing that doesn't have a direct equivalent in Ansible.
  - Mitigation: Use a combination of Ansible assert modules, custom modules, or third-party tools like OSCAP

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing with Vagrant.
  - Mitigation: Replace with Molecule for testing Ansible roles and playbooks

- **Deployment Script Conversion**: The Chef server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for deployment of alternative compliance solutions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): No migration needed, already in Ansible format
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks for deploying alternative compliance solutions
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need modification.
3. The deployment scripts are examples and not used in production environments.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
5. There's no requirement to maintain Chef Automate/Infra Server functionality, only the compliance testing capabilities.
6. The target environment will continue to be Ubuntu 20.04 or compatible systems.
7. The migration will focus on preserving the security compliance checks rather than the specific tools used.