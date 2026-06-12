# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring a secure web server
2. Chef InSpec tests for validating compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS, self-signed certificates, and a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-compliance-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol security validation

- **ssh-compliance-profile**:
    - Description: Chef InSpec profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG validation

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a template for the website. Can be directly incorporated into Ansible.

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance platforms (e.g., AWX/Ansible Tower)
  - Option 2: Deploy open-source compliance tools (e.g., OpenSCAP, Wazuh)

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the same SSL protocol restrictions

- **SSH Hardening**: The SSH compliance profile must be converted to Ansible checks
  - Approach: Create an Ansible role that both configures and validates SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely through Ansible Vault or external certificate management

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Test Execution Flow**: Test Kitchen provides a specific workflow that needs to be replicated
  - Mitigation: Document the new testing workflow with Molecule or other Ansible testing frameworks

- **Deployment Scripts**: The Chef deployment scripts contain specific configuration that needs to be preserved
  - Mitigation: Create equivalent Ansible roles for deployment of compliance tools with the same configuration options

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Convert to a proper Ansible role structure
   - Add documentation and parameterization

2. **poodle-fix playbook** (low risk, already Ansible)
   - Incorporate into the Apache role as a security hardening task
   - Add conditional logic for enabling/disabling specific hardening measures

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks for deploying alternative compliance platforms
   - Ensure all configuration options are preserved

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the same level of compliance testing
2. The current setup is used for demonstration/educational purposes rather than production
3. The SSH compliance profile is intended to be run against the same systems as the web server configuration
4. The deployment scripts are used for setting up a compliance environment, not for the actual systems being tested
5. No external data sources or integrations are present beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
8. There are no specific performance requirements that would affect the migration approach