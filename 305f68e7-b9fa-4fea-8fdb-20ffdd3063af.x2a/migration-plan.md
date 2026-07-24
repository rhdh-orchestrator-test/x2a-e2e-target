# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible role-based approach while preserving the compliance testing functionality currently provided by Chef InSpec.

The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity. The primary challenge will be replacing Chef InSpec with an Ansible-native compliance testing solution.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
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

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration will require updating to use Ansible-native testing tools.
- `index.html`: Static HTML file for the website, can be directly incorporated into Ansible role.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider integrating with OpenSCAP for compliance scanning

- **Test Kitchen**: Replace with Molecule for Ansible role testing:
  - Molecule provides similar functionality but is designed specifically for Ansible roles
  - Will require creating a molecule.yml configuration to replace kitchen.yml

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should preserve:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (disabling SSLv3, enabling TLSv1.2)
  - Secure virtual host configuration

- **SSH Hardening**: The InSpec profile checks SSH security settings. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Implement equivalent compliance checks using Ansible's assert module or Molecule

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Replacing InSpec Testing**: Finding an equivalent Ansible-native solution for compliance testing will be the biggest challenge. Options include:
  - Using Ansible's assert module for basic compliance checks
  - Integrating with Molecule for more comprehensive testing
  - Using ansible-lint for static analysis of playbooks
  - Considering integration with OpenSCAP for compliance scanning

- **Preserving Compliance Reporting**: InSpec provides rich compliance reporting. Migration should ensure:
  - Equivalent reporting capabilities in the Ansible solution
  - Ability to track compliance over time
  - Integration with existing compliance frameworks

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper structure
   - Create role directory structure (tasks, handlers, templates, files)
   - Move inline templates to template files
   - Implement idempotent tasks

2. **poodle_fix.yml** (Priority 1): Incorporate into the Apache role
   - Create a dedicated task file for security hardening
   - Ensure idempotence and proper handlers

3. **InSpec Tests** (Priority 2): Replace with Ansible-native testing
   - Implement equivalent tests using Ansible's assert module or Molecule
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles
   - Create roles for Chef Server and Automate deployment
   - Use Ansible Vault for credential management
   - Implement proper idempotence checks

### Assumptions

1. The primary goal is to migrate from using Chef InSpec for compliance testing to an Ansible-native solution while preserving the existing Ansible playbooks' functionality.

2. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README mentioning it's for "content created by the Technical Product Marketing and Developer Relations teams."

3. The hardcoded credentials in the deployment scripts are for demonstration purposes and will need to be properly secured in the migrated solution.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. The migration should preserve the compliance testing capabilities currently provided by Chef InSpec, including port checking, HTTPS validation, and SSH configuration verification.

6. The current setup uses Test Kitchen for testing, which will need to be replaced with an Ansible-native testing solution like Molecule.