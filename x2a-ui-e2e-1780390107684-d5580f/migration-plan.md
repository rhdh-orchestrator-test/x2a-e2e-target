# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are properly implemented in the new Ansible-only environment

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

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
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible without changes.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set up equivalent monitoring and compliance solutions
  - Consider AWX/Ansible Tower as a replacement for Chef Automate's dashboard functionality

### Security Considerations

- **SSL Configuration**: The current implementation properly configures Apache with TLSv1.2 and disables vulnerable protocols. This should be maintained in the Ansible-only solution.
  - Migration approach: Keep the existing Ansible tasks for SSL configuration

- **SSH Hardening**: The InSpec test verifies that SSH root login is disabled.
  - Migration approach: Create an Ansible task to ensure this configuration and use Ansible's assert module to verify

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Maintain the existing Ansible OpenSSL tasks, but consider adding support for Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's testing syntax to Ansible's assert module or other testing frameworks may require careful translation to maintain the same level of compliance checking.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs to be replicated in the Ansible environment.
  - Mitigation: Consider integrating with tools like OpenSCAP or using Ansible Tower/AWX for reporting

### Migration Order

1. **website_https and poodle_fix playbooks** (low risk, already in Ansible)
   - No migration needed, already in Ansible format
   - Review and optimize according to current Ansible best practices

2. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

3. **Chef Automate/Server deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Consider implementing AWX/Tower as a replacement for Chef Automate

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible for compliance automation, not for production deployment.

2. The InSpec tests are the main value to preserve, as they contain the compliance checks.

3. The deployment scripts for Chef Automate/Server are likely used for demonstration or testing environments, not production.

4. There are no external dependencies or integrations beyond what's visible in the repository.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs.

6. No complex state management or data persistence requirements exist beyond what's visible in the code.

7. The migration is focused on moving to a pure Ansible solution without Chef components.