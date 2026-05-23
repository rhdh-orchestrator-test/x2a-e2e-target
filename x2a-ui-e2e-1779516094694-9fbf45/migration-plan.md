# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test that validates SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Template HTML content for the web server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module and register task results
  - For more complex tests: Integrate with Molecule for testing or Ansible's `uri` module for HTTP checks
  - For compliance testing: Consider migrating to Ansible's built-in security roles or OpenSCAP integration

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the only enabled protocol
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible
  - Convert the InSpec SSH root login check to an Ansible task that enforces the same policy
  - Preserve the STIG compliance metadata as Ansible tags or comments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password') should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with well-structured test conditions
  - Consider using Ansible's built-in testing modules like uri, stat, and command with register

- **Compliance Metadata**: Preserving STIG and CCI compliance information from InSpec tests
  - Mitigation: Use Ansible tags and documentation to maintain compliance metadata
  - Consider integrating with OpenSCAP for more comprehensive compliance testing

- **Chef Server Deployment**: Replacing Chef Automate and Chef Server deployment scripts
  - Mitigation: Create Ansible roles that perform equivalent server setup tasks
  - Consider using existing community roles for Chef server deployment if still needed

### Migration Order

1. **website-https-verify** (low risk, high value): Convert InSpec tests to Ansible assertions
2. **ssh-profile** (low risk, high value): Convert InSpec SSH tests to Ansible assertions
3. **chef-automate-deploy** and **chef-server-deploy** (moderate complexity): Create Ansible playbooks to replace these deployment scripts if still needed

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can remain largely unchanged
2. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of testing
3. The Chef Automate and Chef Server deployment scripts may still be needed in the new environment
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No additional Chef cookbooks or recipes exist beyond what's visible in the repository
6. The security compliance requirements (STIG, CCI) must be preserved in the migrated solution