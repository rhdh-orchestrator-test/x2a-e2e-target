# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS response validation, SSL protocol security checks

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Use Molecule with Testinfra for more comprehensive testing
  - Option 3: Keep InSpec but run it from Ansible using the `command` module

- **Test Kitchen with Vagrant**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible automation platforms:
  - Option 1: Ansible Tower/AWX for enterprise automation
  - Option 2: Ansible Semaphore for lightweight GUI
  - Option 3: GitLab CI/CD with Ansible for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook specifically addresses SSL security by enforcing TLSv1.2. This security hardening should be maintained in the migrated solution.
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider implementing a more robust certificate management solution in the migrated Ansible playbooks, potentially using Let's Encrypt.

- **SSH Security**: The ssh_profile.rb InSpec test enforces SSH security best practices (disabling root login). Ensure these checks are maintained in the migrated testing framework.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the specific assertions and checks being performed. Testinfra provides similar functionality but with different syntax.
  - Mitigation: Create a mapping document for InSpec resources to Testinfra/Molecule equivalents.

- **Chef Automate/Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate's functionality.
  - Mitigation: Conduct a feature comparison between Chef Automate and Ansible Tower/AWX to ensure all required capabilities are covered.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; may need minor updates for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to replace with Ansible equivalents for automation platform deployment.

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment.
2. The hardcoded credentials in the deployment scripts are examples and not used in production.
3. The target environment is Ubuntu 20.04 as specified in kitchen.yml.
4. The Apache configuration is basic and doesn't include complex customizations beyond what's visible in the playbooks.
5. There are no external dependencies or roles being used by the Ansible playbooks.
6. The InSpec profiles are complete and don't reference external profiles or attributes.
7. The deployment scripts are meant for fresh installations rather than upgrades or migrations.
8. There are no specific performance requirements for the web server configuration.
9. The self-signed certificates are acceptable for the use case rather than requiring trusted certificates.
10. The repository is primarily for educational/demonstration purposes based on the README content.