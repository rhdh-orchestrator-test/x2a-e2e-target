# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the InSpec testing capabilities while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

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
    - Key Features: Apache SSL configuration hardening

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Maintain InSpec as a standalone testing tool but integrate with Ansible workflows
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments
  - GitLab/GitHub for version control and CI/CD pipelines

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and disable older protocols
  - Consider updating to include TLSv1.3 support

- **SSH Security**: Preserve the SSH root login restrictions verified by the InSpec tests
  - Implement as Ansible tasks with appropriate assertions
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - Migration should implement Ansible Vault for credential storage
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Consider using Ansible's assert module or maintaining InSpec as a complementary tool

- **Compliance Reporting**: Chef Automate provides compliance reporting that needs an equivalent in the Ansible ecosystem
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with third-party compliance tools

- **Certificate Management**: The current solution uses self-signed certificates generated via Ansible
  - Mitigation: Consider implementing Ansible roles for certificate management with options for both self-signed and CA-signed certificates

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role for better reusability

2. **poodle-fix playbook** (low risk, already Ansible)
   - Integrate into the website-https role as a configurable option
   - Enhance with additional security hardening options

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible Molecule tests or maintain as InSpec
   - Ensure all compliance checks are preserved

4. **Chef Automate/Server deployment** (high complexity)
   - Replace with Ansible Automation Platform deployment
   - Implement equivalent user/organization management

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Vagrant will continue to be used for local development/testing
4. Self-signed certificates are acceptable for the demonstration environment
5. The hardcoded credentials in the Chef deployment scripts are for demonstration purposes only
6. The compliance requirements represented by the InSpec tests must be maintained in any migration
7. The migration will standardize on Ansible while preserving the compliance testing capabilities