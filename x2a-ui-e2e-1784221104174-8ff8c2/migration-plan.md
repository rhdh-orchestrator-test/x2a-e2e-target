# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with equivalent Ansible modules or Molecule tests
  - Consider using ansible-lint for static analysis
  - For compliance testing, consider migrating to OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Molecule for Ansible role testing:
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Migrate Chef Automate functionality to Ansible Tower/AWX
  - Replace Chef Infra Server with Ansible content collections and roles

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache:
  - Maintain the same security hardening (disabling SSLv3, enabling TLSv1.2)
  - Consider updating to also include TLSv1.3 support
  - Migrate the self-signed certificate generation to Ansible crypto modules

- **SSH Hardening**: The InSpec tests verify SSH security:
  - Implement equivalent checks using Ansible's assert module or Molecule
  - Ensure the PermitRootLogin setting is properly enforced in the migrated solution

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh (1 password)
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible equivalents:
  - InSpec has specific testing syntax that needs to be mapped to Ansible assert or Molecule verify
  - For the website_https_verify.rb test, use Ansible's uri module and assert
  - For the ssh_profile.rb test, use Ansible's lineinfile or template module to check SSH configuration

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts:
  - The bash scripts that deploy Chef Automate need to be replaced with Ansible playbooks
  - Consider using the AWX/Tower installer playbooks as a replacement

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
3. **Chef deployment scripts** (high complexity, requires replacement of Chef-specific functionality)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning it's a companion to a white paper.
2. The InSpec tests are used for compliance verification only and don't have dependencies on other Chef components.
3. The deployment scripts contain hardcoded values that would need to be parameterized in a production environment.
4. The target environment is Ubuntu 20.04 as specified in kitchen.yml, but the scripts might be used on other distributions as well.
5. The SSL configuration in the playbooks is intended as a basic example and might need enhancement for production use.
6. There are no external dependencies beyond what's explicitly installed in the playbooks.
7. The migration will maintain the same functionality but using pure Ansible solutions instead of the Chef/Ansible hybrid approach.