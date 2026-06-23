# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module and `command`/`shell` modules with `register` and conditional checks
  - For comprehensive testing: Integrate with Molecule for test-driven development
  - For compliance testing: Consider migrating to Ansible Lint with custom rules or OpenSCAP integration

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality specifically designed for Ansible roles and collections

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks
  - Consider migrating to Ansible Tower/AWX for similar enterprise functionality

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure the Ansible role maintains the same level of TLS security (TLSv1.2 only)
  
- **SSH Security Controls**: The SSH root login check must be preserved
  - Convert the InSpec control to an Ansible task that checks and enforces the same policy
  - Preserve the compliance metadata (STIG IDs, CCI references) in Ansible task documentation

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible assert module with well-structured test conditions
  - Consider custom Ansible modules for complex tests

- **Compliance Metadata**: Preserving STIG and CCI references in Ansible
  - Mitigation: Use structured comments in Ansible tasks and roles
  - Consider developing custom Ansible Lint rules to validate compliance requirements

- **Test Kitchen to Molecule**: Adapting the testing workflow
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
   - Convert to Ansible roles for better organization
   - Update any deprecated syntax or modules

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Ansible assertion tasks or Molecule tests
   - Ensure all security checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to replace Chef Automate/Server deployment
   - Consider if full replacement is needed or if alternative CI/CD tools should be used

### Assumptions

1. The current setup uses Chef InSpec primarily for testing/validation while actual configuration management is done with Ansible
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There is no direct integration with cloud-specific services
4. The security compliance requirements (STIG, CCI) must be preserved in the new implementation
5. The Chef Automate/Server deployment scripts are used for setting up a test environment and not for production deployment
6. No external data sources or databases are being configured by these scripts
7. The migration will maintain the same level of security hardening and compliance validation
8. No custom Chef resources or complex Ruby code is present that would require special handling