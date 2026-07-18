# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The main challenge will be replacing Chef InSpec testing with equivalent Ansible testing solutions while maintaining the same level of compliance validation.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for deploying and testing a secure HTTPS website
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs to be converted to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs to be converted to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP for advanced compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be maintained in the migrated solution.
  - Migration approach: Preserve the same SSL configuration parameters in the Ansible tasks

- **SSH Hardening**: InSpec tests verify SSH root login is disabled. This security check should be maintained.
  - Migration approach: Convert InSpec test to Ansible assert or equivalent testing framework

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Maintain the same certificate generation logic but consider adding options for using proper CA-signed certificates

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup-automate scripts

### Technical Challenges

- **Testing Framework Replacement**: Replacing Chef InSpec with equivalent Ansible testing capabilities.
  - Mitigation: Research and implement the most appropriate Ansible testing framework that provides similar capabilities to InSpec for compliance testing.

- **Maintaining Compliance Validation**: Ensuring the same level of compliance validation is maintained after migration.
  - Mitigation: Create a mapping between InSpec tests and equivalent Ansible tests to ensure complete coverage.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml)
   - Low risk as these are already Ansible playbooks
   - Only need to be restructured to fit the new Ansible project organization

2. **Testing Framework** (chef-and-ansible/tests/*)
   - Medium complexity
   - Convert InSpec tests to Ansible testing framework

3. **Chef Deployment Scripts** (setup-automate/*)
   - Higher complexity
   - Convert Bash scripts to Ansible playbooks for deploying management infrastructure

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. Vagrant will continue to be used for development/testing environments.
3. The security compliance requirements will remain the same after migration.
4. The organization will transition from Chef Automate/Infra Server to an Ansible-based management solution.
5. The current InSpec tests represent the complete compliance requirements.
6. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure credential management in production.