# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web applications. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure HTTPS website with Apache, including SSL certificate generation and configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by updating Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL protocol security validation

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG/STIG)

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef server CLI tools
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert to Ansible Molecule with Testinfra for testing
  - Option 2: Use Ansible assert modules directly in playbooks for validation
  - Option 3: Keep InSpec but run it via Ansible rather than Chef

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with Ansible driver (already in use)

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible AWX/Tower for similar functionality

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the Apache configuration
  - Maintain TLSv1.2 requirement and disable insecure protocols
  - Ensure certificate generation remains secure

- **SSH Hardening**: Preserve the SSH security controls
  - Maintain the PermitRootLogin restriction
  - Ensure compliance with referenced security standards (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible/Testinfra assertions
  - Mitigation: Use Testinfra which has similar syntax and capabilities to InSpec

- **Compliance Validation**: Ensuring the same level of compliance validation in the new testing framework
  - Mitigation: Map each InSpec control to equivalent Ansible assertions with proper documentation

- **Chef Server Deployment**: Converting Chef server deployment to equivalent Ansible functionality
  - Mitigation: Research Ansible AWX/Tower deployment options or create custom Ansible roles for Chef server deployment

### Migration Order

1. **InSpec Tests** (Priority 1, moderate complexity)
   - Convert website_https_verify.rb to Ansible/Testinfra tests
   - Convert ssh_profile.rb to Ansible/Testinfra tests

2. **Test Kitchen Configuration** (Priority 2, low complexity)
   - Update or replace with Ansible Molecule configuration

3. **Chef Server Deployment Scripts** (Priority 3, high complexity)
   - Convert to Ansible playbooks for server deployment

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) can remain largely unchanged
2. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
3. The deployment scripts for Chef server are intended to be migrated to Ansible rather than kept as-is
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements and standards referenced in the InSpec tests must be maintained in the Ansible implementation
6. No additional Chef cookbooks or recipes exist beyond what's visible in the repository
7. The migration does not need to address scaling concerns as the current implementation appears to be for single-server deployments