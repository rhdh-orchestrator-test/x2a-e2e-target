# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with both Chef and Ansible components. The primary focus appears to be on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository includes Ansible playbooks for configuring web servers with HTTPS, Chef InSpec tests for verifying configurations, and bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve replacing the Chef InSpec testing framework with Ansible-native testing solutions and converting the Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **ssh-compliance-test**:
    - Description: Chef InSpec test profile for verifying SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Verifies SSH root login is disabled, compliance with security standards

- **website-https-test**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Verifies port 443 is listening, HTTPS is working, SSL3 is disabled, TLS1.2 is enabled

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples
- `README.md`: Repository overview

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for both on-premises and cloud environments (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider ansible-test for unit testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration
  - Molecule can handle the provisioning, configuration, and verification steps

- **Chef Automate/Infra Server**: Replace with Ansible automation controller (AWX/Tower)
  - Migrate user and organization management to Ansible RBAC
  - Replace Chef server functionality with Ansible inventory and collections

### Security Considerations

- **SSL/TLS Configuration**: The current implementation properly disables SSL3 and enables TLS1.2. This security practice should be maintained in the Ansible migration.
  - Migration approach: Use the same configuration parameters in the Ansible apache2_module task

- **SSH Security**: The InSpec test verifies that SSH root login is disabled.
  - Migration approach: Create an Ansible playbook that configures SSH properly and use Ansible assert or Molecule to verify the configuration

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Use the same Ansible openssl_* modules but consider adding proper certificate management for production environments

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials.
  - Migration approach: Use Ansible Vault to securely store and manage credentials

### Technical Challenges

- **Testing Framework Migration**: Moving from Chef InSpec to Ansible-native testing tools.
  - Mitigation: Map InSpec resources to equivalent Ansible modules and assertions. Use Molecule for integration testing.

- **Chef Server Functionality**: Replacing Chef Server with Ansible automation controller.
  - Mitigation: Document the mapping between Chef Server concepts (cookbooks, roles, environments) and Ansible concepts (playbooks, roles, inventories).

- **Compliance Reporting**: Chef Automate provides compliance reporting capabilities.
  - Mitigation: Integrate Ansible with compliance tools like OpenSCAP or use AWX/Tower for reporting.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they are already in Ansible format
   - Review and optimize existing playbooks
   - Add proper documentation and variable management

2. **Testing Framework** (InSpec tests) - Moderate complexity
   - Convert InSpec tests to Ansible Molecule scenarios
   - Ensure all compliance checks are maintained

3. **Chef Server Deployment** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to replace bash scripts
   - Implement secure credential management with Ansible Vault
   - Set up AWX/Tower as a replacement for Chef Server/Automate

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, based on the README content.
2. The InSpec tests are intended to work with both Chef-managed and Ansible-managed infrastructure.
3. The deployment scripts are templates that would be customized for actual deployments (given the placeholder values for hostnames, usernames, etc.).
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The Apache configuration is relatively simple and focused on HTTPS security rather than complex web application hosting.
6. There are no external dependencies or integrations beyond what's visible in the repository.
7. The migration priority is to maintain the same level of compliance testing while moving to an Ansible-only solution.