# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL/TLS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website-https-compliance**:
    - Description: InSpec tests for verifying HTTPS website configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL/TLS protocol verification

- **ssh-compliance**:
    - Description: InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing

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
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments

### Security Considerations

- **SSL/TLS Configuration**: The current implementation disables SSLv3 and enables only TLSv1.2. Migration should maintain or enhance this security posture, potentially adding TLSv1.3 support.
  - Migration approach: Use the `community.crypto` collection for certificate management

- **SSH Hardening**: The SSH compliance profile checks for disabled root login.
  - Migration approach: Use the `ansible.posix` collection for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The repository heavily uses InSpec for compliance testing. Ansible doesn't have a direct equivalent with the same level of expressiveness for compliance checks.
  - Mitigation: Consider using a combination of ansible-lint, assert modules, and potentially keeping InSpec as a standalone tool invoked by Ansible.

- **Certificate Management**: The current implementation uses the Ansible `openssl_*` modules which have been moved to the `community.crypto` collection.
  - Mitigation: Update playbooks to use the proper FQCN (Fully Qualified Collection Name) for these modules.

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Update module references to use collections
   - Improve variable handling and templating

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Update to use proper collection references
   - Consider integrating with the main website playbook

3. **Compliance Testing** (moderate complexity)
   - Evaluate options for replacing or integrating InSpec tests
   - Implement chosen solution

4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for deploying Ansible Automation Platform or AWX

### Assumptions

1. The primary purpose of this repository is to demonstrate InSpec compliance testing with Ansible, not to provide production-ready infrastructure.
2. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
3. There is no requirement to maintain backward compatibility with Chef Automate or Chef Infra Server.
4. The migration will consolidate all automation into Ansible, eliminating the need for Chef components except potentially InSpec.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives.
6. The SSL/TLS configuration requirements will remain the same or become more stringent.