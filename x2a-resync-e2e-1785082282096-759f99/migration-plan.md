# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance testing, rather than a full production infrastructure codebase. The migration scope is relatively small, focusing on consolidating the existing Ansible playbooks and converting the Chef InSpec tests to Ansible-compatible testing frameworks.

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Technologies**: Chef InSpec, Ansible Playbooks, Bash scripts for Chef Automate/Infra Server deployment

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance testing for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, and SSL/TLS protocol configuration

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for simpler testing
  - Option 3: Convert InSpec tests to Ansible assert tasks for basic compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Consider alternatives:
  - Option 1: Replace with AWX/Ansible Tower for centralized management
  - Option 2: Use GitLab CI/CD or Jenkins for pipeline-based automation
  - Option 3: Use Ansible Automation Platform if enterprise support is required

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture:
  - Maintain TLSv1.2 requirement and disable older protocols
  - Consider upgrading to support TLSv1.3
  - Ensure proper certificate management

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this compliance check is maintained:
  - Convert InSpec SSH tests to Ansible assert tasks or Molecule tests
  - Consider expanding SSH hardening with an Ansible role

- **Credentials Management**: 
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in each deployment script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has a domain-specific language for compliance testing
  - Mitigation: Use Ansible's assert module for simple tests, Molecule with Testinfra for more complex tests

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with Ansible:
  - Challenge: The scripts install and configure Chef-specific components
  - Mitigation: This may not be necessary if the goal is to fully migrate to Ansible; otherwise, convert the bash scripts to Ansible tasks

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, just needs review and potential refactoring
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, just needs review and potential refactoring
3. **InSpec Tests** (Priority 2): Convert to Ansible Molecule tests or assert tasks
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles if needed, or replace with AWX/Tower deployment

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The InSpec tests are meant to validate the configurations applied by the Ansible playbooks
3. The deployment scripts are used for setting up a test environment rather than production infrastructure
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There is no complex data structure or state management required
6. There are no external dependencies beyond what's explicitly included in the playbooks
7. The migration goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
8. No specific compliance frameworks (beyond the SSH example) are being targeted
9. The self-signed certificates are for testing only and would be replaced with proper certificates in production