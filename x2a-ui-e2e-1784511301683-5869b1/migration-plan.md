# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **https-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-compliance-profile**:
    - Description: Chef InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the Apache configuration:
  - Disable vulnerable SSL protocols (SSLv3)
  - Enable only TLSv1.2 as implemented in poodle_fix.yml
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: Preserve the SSH security controls:
  - Disable root login via SSH
  - Maintain compliance with security standards referenced in the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing capabilities currently provided by Chef InSpec:
  - Solution: Either integrate with Ansible's native compliance capabilities or continue using InSpec as a standalone tool invoked by Ansible

- **Self-Signed Certificates**: The current implementation generates self-signed certificates:
  - Solution: Use Ansible's crypto modules to maintain the same functionality

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to an Ansible role for better reusability

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the website HTTPS role as a security hardening task

3. **chef-automate-deployment** and **chef-server-deployment** (moderate complexity)
   - Convert shell scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

4. **https-compliance-tests** and **ssh-compliance-profile** (high complexity)
   - Decide on compliance testing strategy (keep InSpec or migrate to Ansible-native)
   - Implement the chosen approach

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The Test Kitchen configuration is used for development and testing only
3. The hardcoded credentials in the deployment scripts are examples and not used in production
4. The self-signed certificates are for demonstration purposes and would be replaced with proper certificates in production
5. The migration should preserve the compliance testing capabilities while consolidating on Ansible
6. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file