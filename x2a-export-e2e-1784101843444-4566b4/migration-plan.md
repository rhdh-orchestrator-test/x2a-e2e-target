# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
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
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible without changes.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic but with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-test

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible AWX/Tower for enterprise automation platform
  - Ansible playbooks for configuration management

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables vulnerable protocols. This security hardening must be maintained in the migrated solution.
  
- **SSH Security**: The ssh_profile.rb InSpec test verifies that root login via SSH is disabled. This compliance check should be implemented in the Ansible solution.

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing security by integrating with Let's Encrypt or other certificate authorities in the migrated solution.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Use Ansible Vault to secure credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules. The compliance checks must remain equally effective.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting. Ensuring equivalent reporting capabilities in Ansible will be challenging.
  - Mitigation: Explore integration with compliance tools like OpenSCAP or implement custom reporting solutions

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance dashboard and reporting in the Ansible ecosystem.
  - Mitigation: Consider Ansible Tower/AWX with custom dashboards or integration with third-party compliance tools

### Migration Order

1. **website_https.yml** (already in Ansible, low risk)
2. **poodle_fix.yml** (already in Ansible, low risk)
3. **website_https_verify.rb** (convert InSpec tests to Ansible tests, moderate complexity)
4. **ssh_profile.rb** (convert InSpec compliance control to Ansible, moderate complexity)
5. **chef-server-deployment** and **chef-automate-deployment** (convert bash scripts to Ansible playbooks, high complexity)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible for compliance automation, not for production deployment.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. There are no external dependencies beyond what's explicitly installed in the playbooks.
4. The security compliance requirements (STIG standards mentioned in ssh_profile.rb) must be maintained in the migrated solution.
5. The Chef Automate and Chef Infra Server deployment scripts are for demonstration purposes and may not reflect production-ready configurations.
6. No external data sources or databases are being used by these configurations.
7. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure alternatives in production.
8. The self-signed certificates are acceptable for the demonstration environment but would likely need to be replaced with proper certificates in production.