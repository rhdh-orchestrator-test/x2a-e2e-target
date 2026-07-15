# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup, virtual hosts, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **website-compliance-tests**:
    - Description: InSpec tests for verifying HTTPS website configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website testing
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checking
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance and automation platforms
  - Consider AWX/Ansible Automation Platform as replacement

### Security Considerations

- **SSL/TLS Configuration**: Migration must preserve the security hardening that disables vulnerable protocols
  - Approach: Use Ansible's `lineinfile` or `template` modules with identical security parameters

- **SSH Hardening**: Maintain compliance with security standards for SSH configuration
  - Approach: Convert InSpec tests to Ansible assert conditions or separate compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use assert modules in Ansible or maintain InSpec as a verification tool called from Ansible

- **Compliance Reporting**: Maintaining compliance reporting capabilities without Chef Automate
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with third-party tools

- **Test Kitchen Workflow**: Replacing the Test Kitchen workflow for developers
  - Mitigation: Document Molecule usage patterns that mirror existing Test Kitchen workflows

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Simply review and optimize existing Ansible playbook

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and potentially merge with main website configuration playbook

3. **chef-infrastructure-deployment** (moderate complexity)
   - Convert bash scripts to Ansible playbooks for infrastructure deployment

4. **website-compliance-tests** and **ssh-security-compliance** (high complexity)
   - Convert InSpec tests to Ansible assertions or maintain as separate compliance tools

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are intended to run against systems configured by the Ansible playbooks
3. There is no requirement to maintain Chef Automate/Infra Server in the migrated solution
4. The security compliance requirements (e.g., SRG-OS-000112) must be maintained in the migrated solution
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The deployment scripts contain default/example credentials that are not used in production
7. Test Kitchen is currently used for development workflow and testing