# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, primarily due to the need to replace Chef InSpec testing with Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Migration consideration: Can be kept as-is but should be updated to use Ansible's native testing capabilities.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Can be kept as-is but should be integrated with the main playbook.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS website functionality. Migration consideration: Replace with Ansible-native testing (Molecule, assert tasks).
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for SSH security compliance. Migration consideration: Replace with Ansible-native security checks.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For compliance testing: Use ansible-lint with custom rules
  - For infrastructure testing: Use Ansible Molecule
  - For runtime verification: Use Ansible assert tasks within playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Determine if these need to be deployed at all in the new architecture, or if they can be replaced with:
  - Ansible AWX/Tower for orchestration
  - GitLab CI or GitHub Actions for pipeline execution
  - Compliance automation using OpenSCAP or ansible-lint

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration approach: Maintain this security hardening but update to include TLS 1.3 support.

- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration approach: Convert to Ansible-native checks and remediation.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Migration approach: Maintain this functionality but consider adding Let's Encrypt support as an option.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password). Migration approach: Replace with Ansible Vault for secure credential storage.
  - Count of credentials detected: 3 (username, password, organization name in setup scripts)

### Technical Challenges

- **Replacing InSpec Testing**: Chef InSpec provides robust compliance testing that needs to be replaced with Ansible-native solutions. Mitigation strategy: Use a combination of ansible-lint, Molecule, and assert tasks to achieve similar coverage.

- **Maintaining Compliance Standards**: The InSpec tests reference specific compliance standards (SRG-OS-000112, V-38607, etc.). Mitigation strategy: Map these standards to equivalent Ansible checks to maintain compliance reporting.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Consolidate website_https.yml and poodle_fix.yml into a single playbook
   - Update to use Ansible best practices and latest syntax

2. **Testing Framework** (Medium complexity)
   - Replace Test Kitchen with Molecule
   - Convert InSpec tests to Ansible-native testing

3. **Chef Deployment Scripts** (Medium complexity)
   - Convert Bash scripts to Ansible playbooks for Chef deployment
   - Alternatively, determine if Chef deployment is still needed or can be replaced with Ansible Tower/AWX

### Assumptions

1. The primary goal is to consolidate on Ansible and eliminate Chef dependencies where possible.
2. Chef InSpec testing needs to be replaced with Ansible-native testing solutions.
3. The deployment scripts for Chef Automate/Infra Server may still be needed in the new architecture (if not, they could be eliminated entirely).
4. The target environment will continue to be Ubuntu 20.04 or newer.
5. Vagrant will continue to be used for development/testing environments.
6. The security compliance requirements (referenced in InSpec tests) must be maintained in the Ansible solution.
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure credential management.