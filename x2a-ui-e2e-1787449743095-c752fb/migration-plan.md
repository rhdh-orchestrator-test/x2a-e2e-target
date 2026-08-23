# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstration purposes. The repository appears to be a set of examples showing how Chef InSpec can be used alongside Ansible for compliance automation, rather than a full production infrastructure-as-code repository. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure a web server with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The main work will involve standardizing on Ansible for both configuration management and compliance testing, replacing Chef InSpec with Ansible's native testing capabilities or integrating with other testing frameworks compatible with Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance test for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, and SSL/TLS protocol configuration

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Automated deployment of Chef Infra Server

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve the security posture:
  - Ensure continued enforcement of TLSv1.2 or higher
  - Consider updating to also allow TLSv1.3 for improved security
  - Maintain self-signed certificate generation or integrate with Let's Encrypt

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain this compliance check in the new testing framework
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the equivalent assertions and test structures.
  - Mitigation: Use Ansible's assert module for basic tests, and consider integrating with specialized testing tools for more complex scenarios.

- **Chef Automate Deployment**: The shell scripts for deploying Chef Automate and Chef Infra Server would need to be replaced with Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment, or preferably, replace with Ansible AWX/Tower for similar functionality.

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, requires minimal changes
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, requires minimal changes
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing or alternative testing framework
4. **Chef Deployment Scripts** (Priority 3): Replace with Ansible playbooks or consider if they're needed at all in an Ansible-only environment

### Assumptions

1. The repository is primarily for demonstration purposes and not a production infrastructure-as-code repository
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The security requirements include TLSv1.2 for HTTPS and disabled SSH root login
4. The Chef InSpec tests are used for compliance verification rather than for driving configuration
5. The deployment scripts for Chef Automate and Chef Infra Server may not be needed in the migrated solution if moving entirely to Ansible