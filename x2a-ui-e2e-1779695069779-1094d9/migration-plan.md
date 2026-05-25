# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible-based deployment solutions.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope of Chef components and the fact that most infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website-https-verify**:
    - Description: Chef InSpec test for validating HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For simple tests: Use Ansible's `assert` module
  - For complex compliance testing: Integrate with Ansible Lint or Molecule
  - Alternative: Use the ansible-test framework

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles
  - Can use the same Vagrant driver for local testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform
  - Ansible AWX/Tower for web UI and job scheduling
  - Ansible Galaxy for role sharing
  - Ansible Automation Hub for content management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain the same level of security in Apache configurations

- **SSH Security**: Preserve the SSH hardening checks from the InSpec profile
  - Convert the SSH root login check to Ansible assertions
  - Maintain compliance with the referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible's crypto modules with proper secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals
  - For complex tests, consider using Ansible's `command` module with grep/awk and assertions

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs an equivalent in Ansible
  - Mitigation: Consider integrating with tools like Ansible Automation Platform's compliance features
  - Alternative: Use Ansible callback plugins to generate custom compliance reports

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Review and update as needed for best practices
   - No actual migration needed, just validation

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Replace with Ansible playbooks for deploying Ansible Automation Platform
   - Create equivalent user and organization setup in Ansible AWX/Tower

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The InSpec tests are used only for validation and not for remediation
3. There are no external dependencies on Chef beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. There is no requirement to maintain backward compatibility with Chef InSpec after migration
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution