# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a template for the web server. Can be preserved as-is or converted to an Ansible template.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use Ansible assert module
  - For compliance testing: Consider using ansible-lint or integrating with OpenSCAP
  - Alternative: Migrate to Ansible's built-in test modules or Molecule for testing

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH root login check must be preserved in the Ansible equivalent
  - Convert the InSpec control to Ansible assert or ansible-lint rule
  - Maintain compliance with security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing requires careful mapping of test assertions
  - Mitigation: Use Ansible's uri module for HTTP tests and command module with assert for SSL protocol verification

- **Compliance Controls**: Maintaining the compliance metadata and documentation from InSpec controls
  - Mitigation: Use structured comments in Ansible tasks or create separate documentation

- **Chef Server Deployment**: Converting Chef server deployment to equivalent Ansible automation
  - Mitigation: Research Ansible AWX/Tower deployment patterns or create custom roles for similar functionality

### Migration Order

1. **website_https.yml** (already Ansible, no migration needed)
2. **poodle_fix.yml** (already Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible assertions)
4. **ssh_profile.rb** (convert InSpec control to Ansible security check)
5. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible roles/playbooks)
6. **kitchen.yml** (replace with Molecule configuration)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and don't require modification beyond potential security improvements.
2. The Chef InSpec tests are currently used for validation only and don't have dependencies on Chef Infra.
3. There's no requirement to maintain backward compatibility with Chef InSpec after migration.
4. The deployment scripts are used for setting up a test/development environment rather than production systems.
5. No external systems are dependent on the current Chef Automate/Infra Server deployment process.
6. The hardcoded credentials in the deployment scripts are not used in production environments.
7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.