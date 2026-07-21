# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be primarily educational in nature, showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server setup scripts.

The migration scope is relatively small, focusing on:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring the existing Ansible playbooks follow best practices
3. Replacing Chef Automate/Infra Server setup scripts with Ansible equivalents

Given the limited scope and small number of files, this migration could be completed in approximately 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

I have performed thorough searches using file_search for the following patterns:
- `**/manifests/init.pp` (Puppet modules)
- `**/recipes/default.rb` (Chef cookbooks)
- `**/*.psd1` (PowerShell modules)

No files matching these patterns were found in the repository. Therefore, there are no traditional Puppet modules, Chef cookbooks, or PowerShell modules to list in the inventory.

The repository contains the following components that need migration:

- **Chef InSpec Tests**:
  - Description: SSH security profile test that verifies root login is disabled
  - Path: chef-and-ansible/tests/ssh_profile.rb
  - Technology: Chef InSpec
  - Key Features: STIG compliance checking, SSH configuration validation

- **Chef InSpec Tests**:
  - Description: HTTPS website verification test that checks port 443, SSL protocols, and website content
  - Path: chef-and-ansible/tests/website_https_verify.rb
  - Technology: Chef InSpec
  - Key Features: SSL/TLS protocol validation, web content verification

- **Ansible Playbook**:
  - Description: Apache HTTPS website deployment with self-signed certificates
  - Path: chef-and-ansible/website_https.yml
  - Technology: Ansible
  - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **Ansible Playbook**:
  - Description: SSL/TLS security hardening to mitigate POODLE vulnerability
  - Path: chef-and-ansible/poodle_fix.yml
  - Technology: Ansible
  - Key Features: Apache SSL configuration hardening, protocol restriction

- **Chef Setup Script**:
  - Description: Deployment script for Chef Automate and Chef Infra Server
  - Path: setup-automate/deploy-automate.sh
  - Technology: Bash/Chef
  - Key Features: Chef Automate installation, user and organization setup

- **Chef Setup Script**:
  - Description: Deployment script for Chef Infra Server (without Automate)
  - Path: setup-automate/deploy-chef-server.sh
  - Technology: Bash/Chef
  - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Molecule or updating to use pure Ansible testing.

- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples. Will need to be updated to reflect the new Ansible-only approach.

- `chef-and-ansible/index.html`: Simple HTML file used as a template for the website deployment. Can be retained as-is or incorporated into an Ansible role.

- `README.md`: Root documentation file explaining the repository purpose. Will need updating to reflect the migration to Ansible-only.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on setup script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider integrating with pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the kitchen-ansible plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline orchestration

### Security Considerations

- **SSL/TLS Configuration**: The current playbooks enforce TLSv1.2 and disable vulnerable protocols (specifically addressing POODLE vulnerability). This security practice should be maintained in the migrated solution.
  - Migration approach: Use the same configuration in Ansible roles, potentially using the `community.crypto` collection

- **SSH Security**: The InSpec test verifies that SSH root login is disabled, which is a STIG compliance requirement.
  - Migration approach: Create an Ansible role that enforces this configuration and includes assertions to verify compliance

- **Self-signed Certificates**: The current solution generates self-signed certificates using OpenSSL.
  - Migration approach: Use Ansible's `community.crypto` collection for certificate management, consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the modules

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing requires a different approach to test writing.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules/assertions to ensure consistent testing coverage
  - Example: InSpec's `describe port(443)` would become an Ansible task using `wait_for` module with `port: 443`

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible.
  - Mitigation: Consider integrating with compliance tools like OpenSCAP or maintaining InSpec as a testing tool while using Ansible for configuration management

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance dashboard in the Ansible ecosystem.
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and only need review for best practices and potential refactoring into roles.
   - Convert to roles with proper directory structure
   - Update to use Ansible Vault for any sensitive data
   - Add documentation

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert these to Ansible-native testing approaches.
   - Create equivalent tests using Ansible's assert module or Molecule
   - Ensure all compliance checks are maintained

3. **Chef Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for setting up equivalent infrastructure.
   - Create Ansible roles for infrastructure setup
   - Move hardcoded credentials to Ansible Vault
   - Add proper error handling and idempotency

4. **Test Kitchen Configuration**: Update or replace with Molecule for testing the new Ansible roles.
   - Create Molecule scenarios for each role
   - Configure CI/CD integration

### Assumptions

1. The primary goal is to standardize on Ansible as the sole configuration management and testing tool, eliminating the dependency on Chef products.

2. The educational/demonstration nature of the repository will be maintained, showing how to achieve compliance automation with Ansible.

3. The target environment (Ubuntu 20.04) will remain the same after migration.

4. The security requirements (TLS configuration, SSH hardening) will remain the same after migration.

5. The self-signed certificate approach is acceptable for demonstration purposes but may need enhancement for production use.

6. The current Test Kitchen setup with Vagrant is sufficient for testing, but could be enhanced with Molecule for a more Ansible-native approach.

7. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution.

8. The STIG compliance requirements referenced in the InSpec tests (e.g., SRG-OS-000112, V-38607) will need to be maintained in the Ansible implementation.