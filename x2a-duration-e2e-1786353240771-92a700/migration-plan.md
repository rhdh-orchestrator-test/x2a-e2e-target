# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef server deployment scripts. The migration will focus on consolidating everything into pure Ansible, maintaining the compliance testing capabilities currently provided by InSpec.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Apache web server with HTTPS configuration, self-signed certificates, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Deployment script for Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

- **inspec-compliance-tests**:
    - Description: InSpec tests for verifying HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol security verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file (not found in repository but referenced in playbooks)

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - AWX/Ansible Tower for centralized automation platform

### Security Considerations

- **SSL Configuration**: The current implementation configures Apache with TLS 1.2 only, disabling older protocols. This security practice should be maintained in the Ansible migration.
  - Migration approach: Use the same Apache module configuration but with Ansible's template module instead of replace

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Use Ansible's openssl_* modules (already in use) with no changes needed

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create custom Ansible modules or use the assert module with appropriate conditions to match InSpec functionality

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible automation
  - Mitigation: Evaluate if Chef server is still needed; if not, remove. If needed, create Ansible playbooks to deploy Chef server or consider migrating to AWX/Tower

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - Just review and ensure best practices are followed

2. **poodle_fix playbook** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - Just review and ensure best practices are followed

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible playbooks
   - Consider if Chef server is still needed or can be replaced entirely with Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README mentioning "examples" and "companion to a white paper".

2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems, not for testing Chef cookbooks.

3. The setup-automate scripts are used for deploying Chef infrastructure, which may be replaced entirely by Ansible/AWX/Tower.

4. The current implementation uses a mix of technologies (Ansible for configuration, InSpec for testing, Bash scripts for Chef deployment) that could be consolidated into pure Ansible.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the actual deployment could be on any cloud or on-premises infrastructure.

6. The security configurations (especially TLS settings) are important and must be maintained in the migration.

7. There are no complex dependencies between components that would complicate the migration.