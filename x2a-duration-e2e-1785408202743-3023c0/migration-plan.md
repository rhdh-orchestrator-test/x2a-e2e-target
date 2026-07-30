# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require converting to Ansible-native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Will need conversion to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need conversion to Ansible testing framework.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Consider maintaining InSpec as a separate testing tool that can be called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipeline configuration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older protocols (SSLv3)
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile tests must be converted to equivalent Ansible checks:
  - Root login restrictions
  - Protocol version enforcement
  - Authentication methods

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules:
  - Challenge: InSpec provides specialized resources like `ssl()` that don't have direct Ansible equivalents
  - Mitigation: May need to use Ansible's `command` module with custom scripts or maintain InSpec for specialized tests

- **Chef Automate/Server Deployment**: Converting the Chef server deployment scripts to Ansible:
  - Challenge: The scripts install Chef-specific components that may not be needed in an Ansible-only environment
  - Mitigation: Determine if Chef Automate/Server is still needed or if it can be replaced with Ansible Tower/AWX

### Migration Order

1. **website_https.yml** (Priority 1): Low risk, already in Ansible format, just needs restructuring to follow Ansible best practices
2. **poodle_fix.yml** (Priority 1): Low risk, already in Ansible format, just needs restructuring
3. **InSpec Tests** (Priority 2): Moderate complexity, requires converting to Ansible testing framework
4. **Chef Deployment Scripts** (Priority 3): Higher complexity, requires decision on whether to maintain Chef components or replace them

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible
3. The Chef Automate and Chef Server deployment scripts may be optional in the future Ansible-only environment
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The current Vagrant/Test Kitchen setup is for local testing only and not part of a larger CI/CD pipeline
6. No external dependencies or third-party modules are being used beyond what's visible in the repository