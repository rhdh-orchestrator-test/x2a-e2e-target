# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be a demonstration environment showing how Chef InSpec can be used alongside Ansible for compliance automation. Additionally, there are scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be kept largely as-is) and moderate complexity for converting the InSpec tests to Ansible-native solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Ansible assert module for runtime verification
  - Option 3: Integrate with Molecule for comprehensive testing

- **Test Kitchen with Vagrant**: Replace with Molecule for Ansible role testing
  - Molecule supports multiple drivers including Vagrant
  - Provides a more Ansible-native testing workflow

- **Chef Automate/Infra Server**: Replace with Ansible automation platform
  - Ansible AWX/Tower for web UI and job scheduling
  - Ansible Galaxy for role sharing
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible:
  - Use ansible-vault for storing sensitive certificate information
  - Consider integrating with external certificate management systems

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained:
  - Convert InSpec SSH checks to Ansible assert tasks or separate playbooks
  - Implement regular compliance scanning with Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to ansible-vault
  - SSL certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions will require careful mapping:
  - InSpec resource types need equivalent Ansible modules
  - Test logic needs to be reimplemented using Ansible conditionals
  - Solution: Create custom Ansible modules or use community modules that provide similar functionality

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible:
  - Challenge: The scripts deploy Chef-specific infrastructure
  - Solution: Either eliminate this component entirely (if moving fully to Ansible) or create Ansible playbooks that can deploy Chef infrastructure if it's still needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and improve variable naming
   - Implement ansible-vault for sensitive data

2. **Testing Framework** (kitchen.yml): Moderate complexity
   - Replace Test Kitchen with Molecule
   - Set up equivalent test environments

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert InSpec tests to Ansible assert tasks
   - Ensure all compliance checks are maintained

4. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Determine if Chef infrastructure is still needed
   - If not, replace with equivalent Ansible automation platform deployment
   - If yes, convert bash scripts to Ansible playbooks that deploy Chef

### Assumptions

1. The repository is primarily for demonstration purposes showing Chef InSpec with Ansible, not a production environment
2. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements represented in the InSpec tests need to be maintained
5. The Chef Automate and Chef Server deployment scripts may be obsolete after migration to pure Ansible
6. No external dependencies or integrations beyond what's visible in the repository
7. No specific performance requirements for the migrated solution
8. The Apache web server configuration requirements will remain the same