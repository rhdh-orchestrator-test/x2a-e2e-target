# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content verification, SSL protocol security checks

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file for website testing. Migration consideration: Preserve as a test artifact.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible
  - Option 4: Migrate to Ansible Compliance as Code using YAML-based checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and job scheduling
  - Ansible Content Collections for role management
  - Git repositories for version control of playbooks

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate templates for SSL configuration

- **SSH Hardening**: The SSH compliance checks must be maintained
  - Approach: Convert InSpec tests to Ansible assert tasks or maintain as separate compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing functionality currently provided by InSpec
  - Mitigation: Evaluate whether to keep InSpec as a separate tool or migrate to Ansible-native testing
  - If keeping InSpec: Create Ansible playbooks that can install and run InSpec tests
  - If migrating: Develop equivalent tests using Ansible's assert module or other testing frameworks

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Mitigation: Use Ansible's crypto modules to maintain the same functionality

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Convert to a proper Ansible role structure
   - Improve variable handling and templating

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Convert to a proper Ansible role structure
   - Consider combining with the website-https role

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible playbooks to replace the bash scripts for deploying infrastructure management tools
   - Consider using AWX/Tower as a replacement for Chef Automate

4. **InSpec tests** (high complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native)
   - Implement the chosen strategy

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are a critical component that must be preserved in some form
3. The target environment will continue to be Ubuntu-based systems
4. There are no external dependencies or integrations not visible in the repository
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The self-signed certificates are acceptable for the use case (not requiring trusted CA certificates)
7. There are no specific performance requirements that would affect the migration approach