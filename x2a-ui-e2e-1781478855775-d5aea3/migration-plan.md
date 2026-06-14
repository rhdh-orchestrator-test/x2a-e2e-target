# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with HTTPS/SSL setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in SSL configurations
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, SSL protocol validation, SSH root login checks

- **chef-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Maintain InSpec as a standalone compliance tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix
  - Ensure TLSv1.2 is enforced in the migrated Ansible roles
  - Maintain the same level of SSL security in Apache configurations

- **SSH Hardening**: The SSH root login restrictions must be maintained
  - Ensure SSH configuration is properly managed in the migrated Ansible roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use ansible.builtin.assert or community.general.assert modules to perform similar validations
  - Consider maintaining InSpec as a compliance tool if extensive testing is required

- **Chef Automate Deployment**: Replacing Chef Automate functionality
  - Mitigation: Evaluate if Chef Automate is needed or if Ansible AWX/Tower can provide similar functionality
  - If Chef Automate is still required for compliance reporting, create Ansible playbooks to deploy it

### Migration Order

1. **website-https module** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-fix module** (low risk, already in Ansible)
   - Integrate into the website-https role as a security hardening task
   - Ensure idempotency and proper testing

3. **compliance-tests** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or maintain as InSpec
   - Integrate with Ansible CI/CD pipeline

4. **chef-deployment** (high complexity)
   - Determine if Chef Automate/Server is still needed
   - If yes, create Ansible playbooks to replace the shell scripts
   - If no, document the removal and alternative solutions

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The Chef Automate and Chef Infra Server deployment scripts are for demonstration purposes
3. The hardcoded credentials in the deployment scripts are not used in production environments
4. The Test Kitchen configuration is primarily for testing and demonstration
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
6. The migration will standardize on Ansible while potentially maintaining InSpec for compliance testing
7. No external dependencies or complex infrastructure are involved beyond what's visible in the repository