# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use the Ansible `assert` module
  - For more complex compliance testing: Use Ansible Lint or Molecule for testing
  - For comprehensive compliance: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles
  - Can use the same Vagrant driver for local testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the POODLE vulnerability fix
  - Ensure the Ansible playbook continues to enforce TLSv1.2 and disable SSLv3
  - Add additional modern security practices like disabling older TLS versions (1.0, 1.1)

- **SSH Security**: Maintain the SSH root login restriction
  - Convert the InSpec control to an Ansible task that ensures PermitRootLogin is not set to 'yes'
  - Consider adding additional SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Replace with Ansible Vault for secure credential storage
  - Count: 2 credential sets detected (username/password in both deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions
  - Challenge: InSpec provides a domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use a combination of Ansible's assert module, custom modules, and external tools like OpenSCAP

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible
  - Challenge: The script uses Chef-specific commands that need Ansible equivalents
  - Mitigation: Create an Ansible role that performs the same steps using Ansible modules (package, command, template)

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and update to current Ansible best practices
   - Ensure idempotency and proper error handling

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Convert to Ansible roles
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The current Ansible playbooks are working as expected and don't require functional changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements (STIG standards) mentioned in the InSpec tests must be maintained
5. The Chef Automate and Chef Infra Server deployment is still required (not being replaced by another solution)
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives
7. The self-signed certificates are acceptable for the environment (not requiring integration with a certificate authority)