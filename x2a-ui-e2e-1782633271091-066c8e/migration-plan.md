# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-compliance**:
    - Description: Chef InSpec profile for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **ssh-compliance**:
    - Description: Chef InSpec profile for verifying SSH security configuration compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for website testing. Can be preserved as-is or incorporated into Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with tools like Compliance-as-Code or OpenSCAP
  - Option 3: Maintain InSpec as a standalone compliance tool but invoke from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for:
  - Option 1: Deploy alternative compliance platforms (e.g., AWX/Tower)
  - Option 2: Create Ansible playbooks to deploy Chef products if they must be maintained

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Create dedicated Ansible role for Apache SSL hardening with appropriate defaults

- **SSH Hardening**: The SSH compliance checks must be maintained
  - Approach: Create Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault or external secret management

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing or integrating Chef InSpec tests
  - Mitigation: Evaluate ansible-test, molecule verify, or maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Implement Molecule testing framework with appropriate verifiers

- **Deployment Scripts**: The Chef deployment scripts contain hardcoded values and assumptions
  - Mitigation: Create parameterized Ansible roles with appropriate defaults and variables

### Migration Order

1. **website-https** and **poodle-fix** playbooks (low risk, already in Ansible)
   - Refactor into proper Ansible roles with variables and documentation

2. **Compliance Testing** (moderate complexity)
   - Decide on compliance testing strategy
   - Implement chosen approach (ansible-lint, maintain InSpec, or alternative)

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles to replace the deployment scripts
   - Implement proper secret management

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The hardcoded credentials in deployment scripts are examples and not used in production
3. The SSL certificates are self-signed for testing purposes only
4. The compliance profiles are examples and may need enhancement for production use
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There is no external dependency on Chef Automate for compliance reporting
7. The migration should preserve the ability to test infrastructure compliance
8. The SSH compliance profile is intended to be run against the same systems as the web server