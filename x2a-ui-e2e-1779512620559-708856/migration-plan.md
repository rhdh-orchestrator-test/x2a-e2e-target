# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and verify secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Based on the repository analysis, this is a low-complexity migration that should take approximately 1-2 weeks to complete, primarily focused on:
1. Converting InSpec tests to Ansible-native testing solutions
2. Creating Ansible playbooks to replace Chef Automate/Infra Server deployment scripts
3. Ensuring all security compliance checks are maintained during the migration

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG-OS-000112)

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash + Chef
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash + Chef
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML content for the web server. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider integrating with DISA STIG Ansible content for compliance checks

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for integration testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks:
  - Create Ansible roles for configuration management
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable SSL protocols
  - Maintain compliance with security standards

- **SSH Security**: Preserve the SSH security checks from ssh_profile.rb:
  - Disable root login via SSH
  - Maintain compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent test coverage.
  - Mitigation: Consider using Ansible's assert module with well-defined test conditions, or explore community modules that provide similar functionality to InSpec.

- **Compliance Validation**: Ensuring that security compliance checks are maintained during the migration.
  - Mitigation: Create a validation matrix to map each InSpec control to its Ansible equivalent and verify that all security checks are preserved.

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible functionality.
  - Mitigation: Consider using AWX/Ansible Tower as a replacement for Chef Automate/Server, or develop custom Ansible roles to manage configurations centrally.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, primarily to improve idempotence and follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions, ensuring all security checks are maintained.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace these with Ansible playbooks that either deploy alternative configuration management solutions or implement equivalent functionality using Ansible.

4. **Infrastructure Files** (kitchen.yml): Replace with Ansible-native testing framework configuration.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.

2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and follow best practices.

3. The security compliance checks in the InSpec tests are critical and must be maintained in the Ansible-native solution.

4. The Chef Automate and Chef Infra Server deployment scripts are used for demonstration purposes and not for production deployments.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

6. No external dependencies or integrations beyond what is explicitly mentioned in the repository.

7. The migration will focus on preserving functionality rather than enhancing it, with improvements limited to following Ansible best practices.