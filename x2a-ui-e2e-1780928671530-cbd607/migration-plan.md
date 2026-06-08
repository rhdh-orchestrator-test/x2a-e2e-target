# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as most of the configuration is already in Ansible format. The migration will primarily involve:

1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Consolidating the deployment scripts for Chef Automate/Chef Server into Ansible playbooks
3. Ensuring all compliance checks are maintained during the migration

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security tagging with STIG/CCI references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed, can be used as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that enforces TLSv1.2 and disables older protocols.
  
- **SSH Security**: The SSH root login compliance check must be preserved in the Ansible-native testing solution.

- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing a more robust certificate management solution in the Ansible migration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to Ansible-native testing while maintaining the same level of compliance validation will require careful mapping of test assertions.
  - Mitigation: Create a mapping document between InSpec resources and Ansible assertion methods.

- **STIG Compliance**: The SSH profile includes STIG compliance tags that need to be preserved in the Ansible testing framework.
  - Mitigation: Implement custom Ansible roles with appropriate documentation to maintain compliance tracking.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. May need minor updates for best practices.

2. **Chef InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity to convert to Ansible-native testing.

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to convert to Ansible playbooks with proper secret management.

### Assumptions

1. The current implementation assumes Ubuntu 20.04 as the target OS. The migration will maintain this assumption unless otherwise specified.

2. The repository appears to be a demonstration/example of using Chef InSpec with Ansible rather than a production deployment. The migration plan assumes this is for educational/demonstration purposes.

3. The current implementation uses Vagrant for local testing. The migration will need to maintain compatibility with local testing environments.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in a production environment.

5. The migration assumes that the primary goal is to eliminate the dependency on Chef InSpec while maintaining the same level of compliance testing.

6. The SSH compliance profile references RHEL-specific STIG IDs, but the testing environment is Ubuntu-based. This inconsistency should be addressed during migration.