# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure deployment. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary focus will be on:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring the Chef Automate/Infra Server deployment scripts are replaced with Ansible playbooks
3. Maintaining the compliance testing capabilities while standardizing on Ansible

**Timeline Estimate**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance testing for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, and SSL/TLS protocol configuration

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment example
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider integrating with OpenSCAP for compliance scanning

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Use existing Ansible playbooks with minimal modifications

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks that perform the same server setup
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate's functionality

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 only, which should be maintained or updated to include TLS 1.3 in the migrated solution
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider implementing Let's Encrypt integration for production environments
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled; ensure this compliance check is maintained in the Ansible solution
- **Credentials in Scripts**: The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault in the migrated solution:
  - Username/password for Chef user creation
  - Organization name and details

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the compliance requirements and implementing equivalent checks
  - Mitigation: Use Ansible's assert module for simple checks, and consider integrating with tools like OpenSCAP for more complex compliance testing
  
- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting and visualization, finding an equivalent in the Ansible ecosystem
  - Mitigation: Consider AWX/Ansible Tower with compliance plugins or integrate with third-party compliance tools

- **Test Kitchen Workflow**: Preserving the testing workflow currently implemented with Test Kitchen
  - Mitigation: Implement similar workflow using Molecule for Ansible role testing

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and follow best practices
   
2. **Bash Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks, using Ansible Vault for credential storage
   
3. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert these to Ansible-compatible testing frameworks
   
4. **Test Kitchen Configuration**: Replace with Molecule or another Ansible-native testing framework

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment
2. The InSpec tests are used for compliance verification rather than extensive functional testing
3. There are no external dependencies or integrations not visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The deployment scripts are intended for on-premises or generic cloud VMs rather than specific cloud providers
6. The current implementation uses self-signed certificates for demonstration purposes only
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced in a production environment