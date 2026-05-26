# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. The migration scope is relatively small, as most of the infrastructure code is already in Ansible format, with Chef components primarily focused on testing and compliance validation.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef server components
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration consideration: Replace with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for playbook validation
  - Option 3: Maintain InSpec as a standalone tool but invoke it through Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible Test for playbook validation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that enforces TLSv1.2.
- **SSH Security**: The SSH root login compliance check needs to be converted to an equivalent Ansible-based test.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. This should be maintained or improved in the migration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require different approaches to assertions and test structure.
  - Mitigation: Use Ansible assert module or consider tools like Molecule that provide similar testing capabilities.

- **Chef Automate Deployment**: The Chef Automate and Chef Server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for Chef server deployment, or consider if this component is still needed post-migration.

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed
2. **InSpec Tests**: Convert InSpec tests to Ansible-native testing solutions
   - website_https_verify.rb → Ansible assert tasks or Molecule tests
   - ssh_profile.rb → Ansible assert tasks or Molecule tests
3. **Chef Automate Deployment Scripts**: Convert to Ansible playbooks if still needed

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining or improving test coverage.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification.
3. The Chef Automate and Chef Server deployment scripts are still relevant and needed in the migrated solution.
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
5. There are no additional Chef cookbooks or resources not visible in the provided repository structure.
6. The migration doesn't need to address scaling or high-availability concerns as they're not evident in the current implementation.