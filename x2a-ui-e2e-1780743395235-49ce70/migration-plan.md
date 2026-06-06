# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Preserving existing Ansible playbooks with minimal changes
3. Replacing Chef Automate/Chef Server deployment scripts with Ansible equivalents

Given the limited scope and the fact that most of the infrastructure code is already in Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks** for a single developer.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Implement custom testing using Ansible assert modules

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration
  - Molecule provides similar functionality for provisioning test instances and running tests

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles
  - Consider if Chef Automate/Server is still needed or if Ansible AWX/Tower would be a better replacement

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the migrated solution
  - Consider updating to include more recent TLS versions (TLSv1.3)

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible
  - Create an Ansible role that enforces the same SSH security controls
  - Implement equivalent testing using Ansible assert or Molecule/Testinfra

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Consider enhancing with Let's Encrypt integration for production environments
  - Ensure proper certificate permissions are maintained

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents
  - Mitigation: Map InSpec resources to Testinfra or custom Ansible modules; may require additional Python scripting

- **Compliance Reporting**: If Chef InSpec was being used for compliance reporting to Chef Automate
  - Challenge: Finding an equivalent compliance reporting solution in the Ansible ecosystem
  - Mitigation: Consider Ansible AWX/Tower with custom reporting, or integrate with third-party compliance tools

- **Test Kitchen Workflow**: Developers may be accustomed to Test Kitchen workflow
  - Challenge: Learning curve for Molecule or other Ansible testing frameworks
  - Mitigation: Provide documentation and training on new testing workflow

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as they're already in Ansible format
   - May need minor updates to follow current Ansible best practices

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Ansible-compatible testing framework
   - Validate that they provide equivalent coverage

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Replace with Ansible roles for deployment
   - Consider if Chef components are still needed or can be replaced with Ansible alternatives

### Assumptions

1. The primary purpose of this repository is for demonstration/educational purposes rather than production use, based on the README description.
2. The Chef InSpec tests are being used primarily for validation rather than continuous compliance monitoring.
3. There is no complex Chef cookbook structure that needs migration, as the repository focuses on the InSpec + Ansible integration pattern.
4. The deployment scripts for Chef Automate/Server are used for setting up test environments rather than production infrastructure.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production environments.
6. The Test Kitchen configuration is used primarily for testing and demonstration rather than as part of a CI/CD pipeline.
7. There are no external dependencies or integrations beyond what is visible in the repository.
8. The target audience has familiarity with both Chef and Ansible technologies.